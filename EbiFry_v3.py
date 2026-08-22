Using_processor = 100 # 使うスレッド数(安定を取るなら4程度を推奨。高いほど速度は速くなるが、途中で頭打ちする)
SV_PATH = r"C:\MyData\softBV-GUI_v1.2\bin\softBV.exe" # softBV.exeの格納位置 (本体はshareに保存されている)
SP_PATH = r"C:\MyData\softBV-GUI_v1.2\bin\softpath.exe" # softpath.exeの格納位置 (本体はshareに保存されている)
TIME_LIMIT = 3600 # softBV.exe, softpath.exe それぞれの最大実行時間。これを超えると重すぎる計算と判断されてEb計算がスキップされる
TARGET_FOLDER_NAME = "target" # 計算したいICSDを入れるディレクトリ

import csv
import datetime
import glob
import json
import os
import pandas
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymatgen.io.cif import CifParser

import warnings
# 原子位置の丸目誤差に関する警告を無視
warnings.filterwarnings("ignore", message=".*Issues encountered while parsing CIF.*")
# CIFファイル読み取りの際のユーザー警告を無視
warnings.filterwarnings("ignore", category=UserWarning, module = "pymatgen.io.cif")

# NEBスクリーニング前の結晶構造の絞り込み
# 除外するオキソ酸の中心原子(Clならば ClO2, ClO3 などが除外される)
# ex. " C  N  P  Cl "
BANNED_ATOM_GROUP_LIST = " C  N  P  S  Cl  Br  I "
# スクリーニングを行う結晶体積の上限
MAX_STRUCTURE_VOLUME = 2000

def parse_cif(file_path):
    """ CIFファイルから情報取り出し """

    initial_list = []
    # 引用符内を保護しつつ単語を切り出す正規表現
    token_pattern = re.compile(r"'[^']*'|\S+")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # 行頭が # の場合は行全体を1単語として扱う
                if stripped.startswith('#'):
                    initial_list.append(stripped)
                else:
                    tokens = token_pattern.findall(line)
                    initial_list.extend(tokens)

        # セミコロン(;)による結合処理
        final_list = []
        temp_buffer = []
        in_semi_block = False

        for item in initial_list:
            if not in_semi_block:
                # セミコロンが含まれているかチェック
                if bool(re.match(r"^ *; *$", item)):
                    # 1つの要素内に2つ以上の ; がある場合は完結しているとみなす
                    if item.count(';') >= 2:
                        final_list.append(item)
                    else:
                        # ブロック開始
                        in_semi_block = True
                        temp_buffer.append(item)
                else:
                    # 通常の単語
                    final_list.append(item)
            else:
                # セミコロンの閉じ待ち状態
                temp_buffer.append(item)
                if bool(re.match(r"^ *; *$", item)):
                    # 閉じセミコロン発見、結合してリストへ
                    merged = " ".join(temp_buffer)
                    # 連続する空白を1つにする処理
                    cleaned = " ".join(merged.split())
                    final_list.append(cleaned)
                    temp_buffer = []
                    in_semi_block = False
        
        # 閉じ忘れがある場合は残りをそのまま追加
        if temp_buffer:
            final_list.append(" ".join(temp_buffer))

        processed_list = []
    
        for item in final_list:
            # # で始まる要素はスキップ（削除）
            if item.startswith('#'):
                continue
                
            target = item
            
            # ; で囲まれているかチェックして削除
            if (target.startswith(";") and target.endswith(";")):
                target = target[1:-1]
                target = f"'{target}'"
            
            # 加工後の文字列が空でない場合のみリストに追加
            if target:
                processed_list.append(target)

        return processed_list

    except FileNotFoundError:
        return "ファイルが見つかりませんでした。"
    except Exception as e:
        return f"エラーが発生しました: {e}"

def convert_parsed_cif_to_dict(input_list):
    """ parse_cif()で変換されたデータを jsonとして扱えるように変換 """

    result_dict = {}
    i = 0
    n = len(input_list)

    def get_kind(item):
        if item == "loop_": return "K1"
        if item.startswith("_"): return "K2"
        return "K3"

    while i < n:
        kind = get_kind(input_list[i])

        if kind == "K1":
            i += 1
            # K2（キー）を連続して取得
            keys = []
            while i < n and get_kind(input_list[i]) == "K2":
                keys.append(input_list[i])
                i += 1
            
            # K3（値）を連続して取得
            values = []
            while i < n and get_kind(input_list[i]) == "K3":
                values.append(input_list[i])
                i += 1
            
            if keys:
                # K3の数をキーの数の倍数に調整（後半切り捨て）
                num_keys = len(keys)
                num_rows = len(values) // num_keys
                loop_data = []
                
                for r in range(num_rows):
                    row_dict = {}
                    for c in range(num_keys):
                        row_dict[keys[c]] = values[r * num_keys + c]
                    loop_data.append(row_dict)
                
                # メインのキー名は "loop" + 先頭のK2要素名
                # 例: _a なら loop_a となるよう結合
                main_key = f"loop{keys[0]}"
                result_dict[main_key] = loop_data

        elif kind == "K2":
            # 単発のK2: 次がK3ならキー・バリューにする
            key = input_list[i]
            if i + 1 < n and get_kind(input_list[i+1]) == "K3":
                result_dict[key] = input_list[i+1]
                i += 2
            else:
                i += 1 # K3が続かない場合は破棄

        else:
            # 単体のK3は破棄
            i += 1

    return result_dict

def convert_cif_to_json(input_file, output_file):
    """ CIFをJSONファイルに変換 """

    # CIFファイルのパース
    parsed_data = convert_parsed_cif_to_dict(parse_cif(input_file))
    
    # JSON出力
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=4, ensure_ascii=False)
    # print(f"変換が完了しました。出力ファイル: {output_file}")

def find_loop_data(json_data, target_key):
    """
    JSONの中から特定のキーを含むループ(リスト)を探して返す
    """
    for key, value in json_data.items():
        if key.startswith('loop') and isinstance(value, list) and len(value) > 0:
            if target_key in value[0]:
                return value
    return None

def convert_json_to_cif(input_json, output_cif):
    """
    CIFから変換したJSONファイルから、データを絞ったCIFファイルを生成
    """
    
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_cif, 'w', encoding='utf-8') as f:
        # --- 先頭に data_0 を追記 ---
        f.write("data_0\n\n")
        
        # --- 単体データの出力 ---
        single_keys = [
            "_database_code_ICSD",
            "_chemical_name_common",
            "_chemical_formula_structural",
            "_chemical_formula_sum",
            "_chemical_name_structure_type",
            "_cell_length_a",
            "_cell_length_b",
            "_cell_length_c",
            "_cell_angle_alpha",
            "_cell_angle_beta",
            "_cell_angle_gamma",
            "_cell_volume",
            "_space_group_name_H-M_alt",
            "_space_group_IT_number"
        ]
        for key in single_keys:
            if key in data:
                f.write(key + " " + data[key] + "\n")
        f.write("\n")

        # 対称位置の一覧作成
        symmetry_list = []
        symmetry_info = ['_symmetry_equiv_pos_as_xyz','_space_group_symop_operation_xyz']
        for info_name in symmetry_info:
            symop_loop = find_loop_data(data, info_name)
            if symop_loop:
                symmetry_list = [item[info_name] for item in symop_loop]
        if symmetry_list:
            f.write("loop_\n")
            f.write("_space_group_symop_id\n")
            f.write("_space_group_symop_operation_xyz\n")
            for index, symmetry in enumerate(symmetry_list, start=1):
                f.write(f"{index} " + symmetry + "\n")
            f.write("\n")
        
        # 各原子サイトの一覧作成
        atom_site_keys = [
            "_atom_site_label",
            "_atom_site_occupancy",
            "_atom_site_fract_x",
            "_atom_site_fract_y",
            "_atom_site_fract_z",
            "_atom_site_adp_type",
            "_atom_site_B_iso_or_equiv",
            "_atom_site_type_symbol"
        ]
        
        atom_loop = find_loop_data(data, '_atom_site_fract_x')
        if atom_loop:
            # JSONのデータ内に実際に存在するキーだけを抽出（スキップ処理）
            available_keys = [k for k in atom_site_keys if k in atom_loop[0]]
            
            if available_keys:
                f.write("loop_\n")
                # K4 (データ名) の出力
                for k in available_keys:
                    f.write(k + "\n")
                
                # K5 (具体的なデータ) の出力
                for item in atom_loop:
                    row_values = []
                    for k in available_keys:
                        # データが存在しない場合は "." で補完
                        row_values.append(item.get(k, "."))
                    f.write(" ".join(row_values) + "\n")
                f.write("\n")

    print(f"CIFファイルの生成が完了しました。出力ファイル: {output_cif}")

def judge_nearest_neighbor_oxygen(cif_path):
    """ スクリーニングを行うべき構造かを判定 """
    print(os.path.basename(cif_path))

    try:
        parser = CifParser(cif_path, occupancy_tolerance=1.005)
        structures = parser.parse_structures(primitive = True)
        structure = structures[0]
    except Exception as e:
        return f"strange CIF file (ex. too big occupancy) : {e}"

    # 格子体積が一定以上かを判定する
    if MAX_STRUCTURE_VOLUME:
        if structure.volume > MAX_STRUCTURE_VOLUME:
            return f"too big structure ({structure.volume:.0f} A^3)"
    
    # CO3, NO3ような原子団を含むかを判断する
    # 具体的にはC,Nなどの最近接原子がOであるかを判定する
    targets = set(BANNED_ATOM_GROUP_LIST.split())
    for site in structure:
        if site.species_string in targets:
            # 十分に広い半径で近接原子を取得
            neighbors = structure.get_neighbors(site, r=3.0)
            
            if neighbors:
                nearest_neighbor = neighbors[0]
                if nearest_neighbor.species_string == "O":
                    return f"containing banned atomic group (center:{site.specie.symbol})"
                    
    return None

def read_energy_barriers(target_dir):
    """
    生成された 'BVPA_gui.csv' を読み込み、1D, 2D, 3Dのエネルギー障壁(Eb)を取得する。

    Args:
        target_dir (str): 計算結果が保存されたディレクトリ
        
    Returns:
        list: [Eb_1Dの値, Eb_2Dの値, Eb_3Dの値]
    """
    csv_path = os.path.join(target_dir, "BVPA_gui.csv")

    if not os.path.exists(csv_path):
        return None
    
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    eb_values = []
    # 1D, 2D, 3Dの各次元について検索して値を取得
    for dimension in ['1D,', '2D,', '3D,']:
        # 該当する次元の行を抽出
        target_line = next((line for line in lines if dimension in line), None)
        if target_line:
            # カンマまたは空白で分割し、2番目の要素(値)を取得
            split_line = re.split(r",|\s", target_line)
            eb_value = split_line[1]
            #print(f"Eb({dimension.strip(',')}) = {eb_value} eV")
            eb_values.append(eb_value)
        else:
            print(f"Warning: {dimension} not found in BVPA_gui.csv")
            eb_values.append("")

    return eb_values

def initialize_and_format_cifs(cif_rawdir, cal_dir, output_dir):
    """ ICSDで得られたCIFのフォーマット """

    target_keys = [
        "_chemical_formula_sum",
        "_chemical_formula_structural",
        "_chemical_name_structure_type",
        "_database_code_ICSD",
        "_space_group_name_H-M_alt",
        "_space_group_IT_number"
    ]

    cif_files = glob.glob(os.path.join(cif_rawdir, "*.cif"))
    cif_names = []
    result_data = []

    if not cif_files:
        print("CIFファイルが見つかりませんでした。")

    else:
        print(f"{len(cif_files)} 個のCIFファイルが見つかりました。処理を開始します...")
        os.makedirs(cal_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        for i, target_cif_filepath in enumerate(cif_files):
            dir_name = f"{i:08}"
            cif_savedir = os.path.join(cal_dir, dir_name)
            os.makedirs(cif_savedir, exist_ok=True)
            target_cif_filename = os.path.splitext(os.path.basename(target_cif_filepath))[0]
            result_json_filepath = os.path.join(cif_savedir, f"{target_cif_filename}_refined_JSON.json")
            result_cif_filepath = os.path.join(cif_savedir, f"{target_cif_filename}_refined_CIF.cif")
            
            try:
                convert_cif_to_json(target_cif_filepath, result_json_filepath)
                convert_json_to_cif(result_json_filepath, result_cif_filepath)

                with open(result_json_filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 1行分のデータを辞書として作成
                row_dict = {'Filename': target_cif_filename}
                for key in target_keys:
                    # キーが存在しない場合は None を入れて pandas 側で NaN として扱う
                    row_dict[key] = data.get(key, None)

                single_info = [
                    dir_name, target_cif_filename, row_dict["_chemical_formula_sum"], row_dict["_chemical_formula_structural"], 
                    row_dict["_chemical_name_structure_type"], row_dict["_database_code_ICSD"], row_dict["_space_group_name_H-M_alt"], row_dict["_space_group_IT_number"]
                ]
            except Exception as e:
                print(f"ファイル {os.path.basename(target_cif_filepath)} のフォーマット処理中にエラーが発生しました: {e}")
                continue

            cif_names.append(target_cif_filename)
            result_data.append(single_info)

        # 抽出したデータからDataFrameを作成
        RESULT_CSV_INI = "result_initial.csv"
        columns = [
            "dir_name", "file_name", "formula_sum", "formula_structural", 
            "name_structure_type", "ICSD_ID", "space_group_name", "space_group_IT_number"
        ]
        df = pandas.DataFrame(result_data, columns=columns, index=cif_names)
        try:
            df.to_csv(os.path.join(output_dir, RESULT_CSV_INI), encoding='utf-8-sig')
        except Exception as e:
            print(f"{RESULT_CSV_INI} 作成中に失敗しました。ファイルが開かれている可能性があります。: {e}")

        return df

def run_SoftBV(task):
    """ スレッドの実行単位 """
    filename = task["filename"]
    directory = task["CIF_directory"]
    result = [os.path.basename(directory), filename]
    try:
        subprocess.run(task["cmd1"], cwd = directory, timeout = TIME_LIMIT)
        subprocess.run(task["cmd2"], cwd = directory, timeout = TIME_LIMIT)
        Eb_list = read_energy_barriers(directory)
    except subprocess.TimeoutExpired:
        print(f"計算時間が {TIME_LIMIT}s を超えたため、計算をスキップします")
        return result + ["", "", "", "too long calculation time"]
    except Exception as e:
        print(f"BVE計算での予期せぬエラー ：{e}")
        return result + ["", "", "", "unknown error"]
    if Eb_list:
        return result + Eb_list + [""]
    return result + ["", "", "", "no BVPA_gui.csv"]

def write_to_csv(csv_path, content):
    try:
        with open(csv_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(content)
    except Exception as e:
        print(f"csvファイルの書き込みで失敗しました。: {e}")
        return e
    return None

def main():
    print(f"BVEスクリーニング開始: {datetime.datetime.now()}\n")

    # 計算における各ファイルのパス。
    BASE_DIR = os.getcwd() 
    CIF_RAW_DIR = os.path.join(BASE_DIR, TARGET_FOLDER_NAME)
    CAL_DIR = os.path.join(BASE_DIR, "cal_dir")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output_dir")

    # CIFのフォーマットの実行
    fotmatted_cifs_df = initialize_and_format_cifs(CIF_RAW_DIR, CAL_DIR, OUTPUT_DIR)
    print(fotmatted_cifs_df)

    # 結果を出力するcsvの作成
    CSV_NAME = "result.csv"
    csv_path = os.path.join(OUTPUT_DIR, CSV_NAME)
    err = write_to_csv(csv_path, ["dir_name", "file_name", "Eb_1D", "Eb_2D", "Eb_3D", "note"])
    if err: # CSVの作成に失敗した場合は途中終了
        return

    # 並列処理の準備
    ION = "O"
    VALENCE = "-2"
    max_parallel = min(os.cpu_count() or 1, Using_processor)
    tasks = []
    removed_file_num = 0
    for dir_name, file_name in zip(fotmatted_cifs_df["dir_name"], fotmatted_cifs_df["file_name"]):
        cif_dir = os.path.join(CAL_DIR, dir_name)
        cif_filepath = os.path.join(cif_dir, file_name + "_refined_CIF.cif")
        cube_filepath = os.path.join(cif_dir, file_name + "_refined_CIF.cif.cube")

        # スクリーニングを行う必要のない構造を除外
        note = judge_nearest_neighbor_oxygen(cif_filepath)
        if note:
            removed_file_num += 1
            print(f"{file_name}はスクリーニング対象から外されました。理由：{note}")
            write_to_csv(csv_path, [dir_name, file_name, "", "", "", note])
        else :
            cmd1 = [SV_PATH, "--gen-cube", cif_filepath, ION, VALENCE]
            cmd2 = [SP_PATH, "--cube", cube_filepath, "--cif", cif_filepath, ION, VALENCE, "--path", "--gui"]
            tasks.append({"cmd1": cmd1, "cmd2": cmd2, "CIF_directory": cif_dir, "filename": file_name})

    print(f"前処理完了。{len(fotmatted_cifs_df)}ファイル中{len(fotmatted_cifs_df)-removed_file_num}ファイルに対してBVEスクリーニングを行います。  start time: {datetime.datetime.now()}\n")

    if (not os.path.exists(SV_PATH)) or (not os.path.exists(SP_PATH)):
        print("softBV.exe または softpath.exe が見つかりません。パスを確認してください。")
        return

    # softBVの実行部分
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = [executor.submit(run_SoftBV, task) for task in tasks]
        
        # 終わったものから順次csvに追記
        for future in as_completed(futures):
            result = future.result()
            err = write_to_csv(csv_path, result)
            if not err:
                print(f"{result[0]}, {result[1]}  End time: {datetime.datetime.now()}\n")

if __name__ == "__main__":
    with open("time.txt", 'w', encoding='utf-8') as file:
        file.write(f"start time:{datetime.datetime.now()}\n")
    main()
    with open("time.txt", 'a', encoding='utf-8') as file:
        file.write(f"end time:{datetime.datetime.now()}\n")
    print("すべての処理が終了しました")
