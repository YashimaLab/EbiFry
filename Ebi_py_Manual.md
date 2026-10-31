# ebi.py 🦐

2020/4/30 安井 雄太

2026/10/31 益山(Githubへの移動のため微調整) 

## スクリプトの概要
手作業でエネルギー障壁やボトルネックサイズを出すのは非常に時間がかかります。間違いも起こります。そこでsoftBV.exeの使用過程を自動化するために開発したのが「Energy Barrier Investigator」、略してebi.py🦐です。

## 動作環境
* 動作確認: SoftBV CUI 1.0，およびGUI1.1の中身のsoftBV.exe
* \+ Powershell (PyCifRW 4.4.3，python 3.8.5 導入済みが条件)
* pymatgen ver. 2020.12.18

多分2021.2.16までは大丈夫だが、それ以降は不可 (pymatgenが大幅な仕様変更を行い、後方互換性が保たれなくなった)
これにあった環境を別途作りたい方は下の手順で環境を分離するのが良いでしょう。  
[venvの使い方ーGSASとその他のPython環境衝突について](https://docs.google.com/document/d/1nx2Fjqmi250f-LUkkz9GfwukTSiymG_Pqmv0ddDi078/edit#heading=h.vdmum2qo4i6c)

Ebi.py本体の現在の最新バージョンは1.0.3 (2020/4/21)です。

## 使い方

1) softBV コマンドラインバージョン for windowsをダウンロードし，解凍します。  
   [http\://www\.dmse.nus.edu.sg/asn/softBVCL.html](http://www.dmse.nus.edu.sg/asn/softBVCL.html)  
   ここに入っているsoftpath.exeがないといけない設計になっているため，GUIとは別に用意する必要があります。これを解凍して好きなところに置いておきます。  
   bin の中身は下手にいじらないほうがよいです。  
2) [Python初心者向け速習](https://docs.google.com/document/d/1tSxYH5qJQWGm_KlvlwGZLvsO_pZ9gdCqJli-Vmx7d3E/edit) にしたがってPythonを入れます。  
   ーーーーーーーーーー講習前にやること　ここまでーーーーーーーーーーー  
3) Visual Studioのダウンロード
   [https\://visualstudio.microsoft.com/ja/downloads/](https://visualstudio.microsoft.com/ja/downloads/)  
   ↑これでダウンロードでると思います  
4) ↑の6. モジュール の操作にしたがってpymatgen,PycifRW，  
5)  numpy, pprintを入れます。  
   例: pip install pymatgen  
   追記: 後方互換の関係で、pymatgenは古いバージョンを入れてください。具体的には、pip install pymatgen==2020.12.18 とすると良いです。  
6) ebiと付属するデータをダウンロードしてください↓　ebi\_1\_0フォルダごとまとめて  
   [https\://drive.google.com/drive/folders/15WsMEpccpvhtMqb7ArtVdCmAdxEaZjhE](https://drive.google.com/drive/folders/15WsMEpccpvhtMqb7ArtVdCmAdxEaZjhE)  
7) ebi.py　をメモ帳かなにかで開き，softBV.exeとsoftpath.exeの場所設定を行います。  
   最初のほうにこんなのがあると思います。
   
   ```python
      # ↓softBVとsoftpathの絶対パスを指定
      SV_dir = "C:¥¥softBVC¥¥bin¥¥softBV.exe"
      SP_dir = "C:¥¥softBVC¥¥bin¥¥softpath.exe"
   ```   

   これがソフトの場所設定になります。
   コマンドラインバージョンのなかにsoftBV.exeとsoftpath.exeが入ってるフォルダがあるので，そこを開いて上のバーをクリックするとこんな感じのが表示されるのでそれをコピーします。  

   <img src="image_for_md\address_bar.png" width="50%">

   で，￥マーク(Google drive上ではバックスラッシュに見えている)を2重にします。最後にsoftBV.exe, softpath.exeを入れてダブルクォーテーションマークで囲えばOKです。  
   SV\_dir \= "C:¥¥softBVC¥¥bin¥¥softBV.exe"  
   バックスラッシュと円マークは同じ文字コードなため化けますので注意してください。最近はどっちも対応するようになってるという話もあるがあまり深く確認はしていません。[参考](https://ja.wikipedia.org/wiki/%E3%83%90%E3%83%83%E3%82%AF%E3%82%B9%E3%83%A9%E3%83%83%E3%82%B7%E3%83%A5#%E3%83%90%E3%83%83%E3%82%AF%E3%82%B9%E3%83%A9%E3%83%83%E3%82%B7%E3%83%A5%E3%81%A8%E5%86%86%E8%A8%98%E5%8F%B7)   
   また，￥マークを2重にする理由はエスケープ(特殊文字ではないですよアピール)させるためです [参考](https://www.javadrive.jp/python/string/index2.html)  
8) 必要に応じてcoord\_func と cube\_cleanの数値も編集します。  
   前者は配位数の解析アルゴリズムを変えるものです。v1.1.x以降ではひとまず coord\_func \= 1 (EconNN)を推奨します。  
   ebi v1.0.x(x \= 0-3)ではcoord\_func \= 0 と同じ扱いでした。デフォルトではそうなってます。どちらの配位数計算アルゴリズムなのかは，v.1.1.x以降では\_ebi\_results.csv に書き出される仕様になっています。  
9) ebi.py　と同じフォルダに計算したいcifを入れます。  
   \_pop\_ox\_numbers.csv，\_ionic\_radius\_data.csv, gh\_cleaning.py, ebi\_preprocess.py　はebi.pyが参照するファイルなので消さないでください。  
   ebi\_preprocess.pyはv1.2.0から追加されました。

10) cd ……でebi.pyのディレクトリに移動します。  
11) python ebi.py　を打ってエンターキーを押せば走ります。同じフォルダにあるcifすべてで計算します。

   ```bash
      > cd C:\Users\yasui\Dropbox\tools (それぞれのデータ保存場所に変えること)
      > python ebi.py
   ```

12) 結果が\_ebi\_results.csv に吐き出されます。いろんな列がありますが，まず見るべきは初期状態Excelで列Gの「Eb / eV」です。あと列Aがファイル名，列Bが組成になっています。  
13) Ebがby \--ghというのとby BVPA の2種類あります。BVPAが基本正しそうなのでそちらを書くのが吉です。ただし，**まだ調査が足りてないので気をつけて，BVPAという機能を使ってることを進捗報告のときはどこかに明記してください。**先生に聞かれたら「安井ってやつがsoftBVのpathway analyzerを取り入れたものです」と答えてください。  
    BVPAの吐き出すデータを安井が独自に切り取る形をとっているので，データ切り抜き面のバグがあるかもしれません。調査中です。  
14) そしたらEbでソートして，化合物数と障壁でまとめてみたりしましょう。こんなかんじで。

    <img src="image_for_md\Ebi_Graph.png" width="50%">

　なお，まとめやすさや計算時間を考慮して，cif200-300個ずつぐらいで計算するのが良いと思います。エラーさえでなければまとめてやってもいいんですがICSDのcifがイマイチで止まることもたまにあって……。  
最後は結果のcsvをコピーして1つのファイルにまとめる。で，班員と話し合ったりして実験対象を決める。

## エラー報告

　エラーは積極的に報告してください。ここに対処法を書いていきます。 (名前書いてね)  
　9割はICSDのcifがイマイチなために起こります。cifの文法がおかしいときにはcif reading errorと出るように作ってあります。

計算が正常に終了したら「\*\*ebi.py:  all calculation has finished\!」が表示されます。これが表示されてなかったら計算中か，エラーで止まっています。

### インストールエラー1: numpy関連

numpy 1.19.4だとWindowsではインストールでバグることが知られている。  
pip install numpy==1.19.3　とするとよい

### インストールエラー2: PEP517

pip install pymatgenして  
ERROR: Could not build wheels for spglib which use PEP 517 and cannot be installed directly  
と出るときは  
python \-m pip install \--no-use-pep517 pymatgen  
とすると解決

### softpath.exeがまったく動かない問題 (Suzuki)

(さらに作動させようとするとregex2.dll関連のエラーが出る)  
・csvファイルを開きながら実行したらsoftpassの計算ができませんでした。  
・計算させたらregex2.dllを入れろという警告が出ました。いれたら動きました。  
・失敗したdataを共有リンク先におきました。  
・[https\://drive.google.com/open?id=1V7PY8WgTDCDxxgggxLYeq\_NhliY\_yL7r](https://drive.google.com/open?id=1V7PY8WgTDCDxxgggxLYeq_NhliY_yL7r)

参考情報  
[http\://gnuwin32.sourceforge.net/packages/regex.htm](http://gnuwin32.sourceforge.net/packages/regex.htm)   
[https\://mikiyaokada.hatenadiary.org/entry/20091230/1262153327](https://mikiyaokada.hatenadiary.org/entry/20091230/1262153327) 

なお，softpath.exeは体感2割ぐらいcubeファイルが読み込めずエラーが出るので，これが原因と決めつけるまえにさまざまなcifで試してほしいです。  
ただしsoftpath.exeの書き出しが失敗してもebi.pyは止まらないようにしてあります。 (やすい)

### \_cell\_length\_a が読み込めない的なの (George)

原因不明。たぶんcifファイルの文法が間違ってる。loop\_を入れなければならないところに入ってない。  
VESTAでcifを書き出し直して解決。  
大抵のICSD cifはここは大丈夫。

### Permission Error

同じディレクトリの\_ebi\_results.csvを開きっぱなしにしてるから起こる。書き込み禁止による。  
そのExcelを閉じることで解決。

### Traceback 〜〜 が表示されて止まる

　これはsoftBVのエラーでなくPythonがebi.pyを動かすときのエラーです。Pythonにはエラーが出たとき，その直前の動作を遡って(Traceback)表示してくれる機能があります。よく読み，何行目にどんな感じのエラーがあったのかを見ましょう。

　cifの読み込みでエラーが出た時は  
        print("\*\*ebi.py: cif reading error on " \+ (cifファイル名))  
        print("\*\*ebi.py: this script stop.")  
　で止まるようにしてあります。Tracebackが表示されていたとしてもこれらのメッセージが最後に表示されたときはcifの文法に問題があります。体感7割は論文タイトルの書き方に問題がある。

## このスクリプトを使った結果を論文にするとき

このスクリプトは以下の外部プログラム要素を含んでいますので，それらの論文を引用するとともに，それらのソフトのライセンスもご一読ください。  
学会発表でもどこかに記載しておくほうがよいと思われます。  
softBV-command line version: [http\://www\.dmse.nus.edu.sg/asn/softBVCL.html](http://www.dmse.nus.edu.sg/asn/softBVCL.html)    
H. Chen, L.L. Wong, S.Adams; SoftBV \- a software tool for screening the materials genome of inorganic fast ion conductors. *Acta Crystallogr.* B 75 (2019), 18-33. [https\://doi.org/10.1107/S2052520618015718](https://doi.org/10.1107/S2052520618015718) (as the source of the code)  
H. Chen, S. Adams; Bond softness sensitive bond-valence parameters for crystal structure plausibility tests. *IUCrJ* 4 (2017) 614-625. [https\://doi.org/10.1107/S2052520618015718](https://doi.org/10.1107/S2052520618015718)  (as the source of the BV parameters)

(直接呼び出してるわけではないが) VESTA [https\://jp-minerals.org/vesta/jp/download.html](https://jp-minerals.org/vesta/jp/download.html)   
K. Momma and F. Izumi, VESTA 3 for three-dimensional visualization of crystal, volumetric and morphology data, *J. Appl. Crystallogr.*, 2011, 44, 1272–1276.  
10.1107/S0021889811038970

PyCifRW [https\://pypi.org/project/PyCifRW/](https://pypi.org/project/PyCifRW/)  
Hester, J. R., A Validating CIF Parser: PyCIFRW.  *J. Appl. Crystallogr.* 2006, 39 (4), 621–625. 10.1107/S0021889806015627.

Pymatgen [https\://pymatgen.org/index.html\#](https://pymatgen.org/index.html#)   
P. Ong, W. D. Richards, A. Jain, G. Hautier, M. Kocher, S. Cholia, D. Gunter, V. L. Chevrier, K. A. Persson and G. Ceder, Python Materials Genomics (pymatgen): A robust, open-source python library for materials analysis, *Comput. Mater. Sci.*, 2013, 68, 314–319.  
10.1016/j.commatsci.2012.10.028

EconNN　もしくは　VoronoiNN  
EconNN:  Hoppe, Rudolf. “Effective coordination numbers (ECoN) and mean fictive ionic radii (MEFIR).” Zeitschrift für Kristallographie-Crystalline Materials 150.1-4 (1979): 23-52.  
VoronoiNN: O’Keeffe, M. A proposed rigorous definition of coordination number. Acta Crystallogr. A 1979, 35, 772–775, DOI: 10.1107/S0567739479001765.

それらのベンチマーク  
Pan, H. et al. Benchmarking Coordination Number Prediction Algorithms on Inorganic Crystal Structures. doi:10.26434/chemrxiv.12508229.v1

numpy  
S. Van Der Walt, S. C. Colbert and G. Varoquaux, The NumPy array: A structure for efficient numerical computation, *Comput. Sci. Eng.,* 2011, 13, 22–30.

## 動作確認

python 3.7.4  
PyCifRW 4.4.1  
Pymatgen 2020.1.28  
numpy 1.17.2  
pprint 0.1

動作環境  
\# 動作確認: SoftBV CUI 1.0，およびGUI1.1の中身のsoftBV.exe  
\# \+ Powershell (PyCifRW 4.4.3，python 3.8.5 導入済みが条件)  
\# pymatgen ver. 2020.12.18

下でも可  
python 3.8.5   
Package             Version  
\------------------- \----------  
argon2-cffi         20.1.0  
async-generator     1.10  
attrs               20.3.0  
backcall            0.2.0  
bleach              3.2.1  
certifi             2020.12.5  
cffi                1.14.4  
chardet             4.0.0  
cif2cell            2.0.0a3  
colorama            0.4.4  
cycler              0.10.0  
decorator           4.4.2  
defusedxml          0.6.0  
entrypoints         0.3  
future              0.18.2  
idna                2.10  
ipykernel           5.4.2  
ipython             7.19.0  
ipython-genutils    0.2.0  
jedi                0.17.2  
Jinja2              2.11.2  
json5               0.9.5  
jsonschema          3.2.0  
jupyter-client      6.1.7  
jupyter-core        4.7.0  
jupyterlab          2.2.9  
jupyterlab-pygments 0.1.2  
jupyterlab-server   1.2.0  
kiwisolver          1.3.1  
MarkupSafe          1.1.1  
matplotlib          3.3.3  
mistune             0.8.4  
monty               4.0.2  
MouseInfo           0.1.3  
mpmath              1.1.0  
nbclient            0.5.1  
nbconvert           6.0.7  
nbformat            5.0.8  
nest-asyncio        1.4.3  
networkx            2.5  
notebook            6.1.5  
numpy               1.19.3  
packaging           20.8  
palettable          3.3.0  
pandas              1.1.5  
pandocfilters       1.4.3  
parso               0.7.1  
pickleshare         0.7.5  
Pillow              8.0.1  
pip                 20.3.3  
plotly              4.14.1  
prometheus-client   0.9.0  
prompt-toolkit      3.0.8  
PyAutoGUI           0.9.52  
PyCifRW             4.4  
pycparser           2.20  
PyGetWindow         0.0.9  
Pygments            2.7.3  
pymatgen            2020.12.18  
PyMsgBox            1.0.9  
pyparsing           2.4.7  
pyperclip           1.8.1  
PyRect              0.1.4  
pyrsistent          0.17.3  
PyScreeze           0.1.26  
python-dateutil     2.8.1  
PyTweening          1.0.3  
pytz                2020.5  
pywin32             300  
pywinpty            0.5.7  
pyzmq               20.0.0  
requests            2.25.1  
retrying            1.3.3  
ruamel.yaml         0.16.12  
ruamel.yaml.clib    0.2.2  
scipy               1.5.4  
Send2Trash          1.5.0  
setuptools          47.1.0  
six                 1.15.0  
spglib              1.16.0  
sympy               1.7.1  
tabulate            0.8.7  
Tcl                 0.2  
terminado           0.9.1  
testpath            0.4.4  
tornado             6.1  
traitlets           5.0.5  
uncertainties       3.1.5  
urllib3             1.26.2  
wcwidth             0.2.5  
webencodings        0.5.1

## 更新履歴

2020/4/11 ebi.py 1.0.0 リリース。ドキュメント作成開始。  
2020/3月ごろ ebi\_beta.py一応完成。--ghだけでなくsoftpath.exeを使うようにプログラムを一新しました。各機能を八割がた関数化しました。ボトルネックサイズを算出する機能をつけました。これをv1.0.0 とする。  
2019年10月ごろのcif2Eb.py : \--gh で障壁を出していました

## 細かい技術の話

### 計算のときに自動生成されるファイル

　ebi.pyと同じディレクトリに入っているcifすべててで計算するので，ghコマンドで生成されるgh.cifも計算してしまいます。計算が正常に進んでいればそのキーワードを最後に含むファイルは消してくれますが，エラーで終了すると残ってしまいます。

### Ebの算出に使ってる機能について
　Eb (BVPA)はsoftpath.exeを使っています。これはsoftBV-GUIのpathway analyzer機能と基本同じだと思われます。  
　また，softpath.exeによって生成されるBVPAファイルも\_ebi\_bvpaというフォルダに組成付きで保管しています。詳しい解析を行う追加のスクリプトでも作るかもしれません。matplotlibを使ってpathwayを視覚化もできるかもしれませんがハードルが高くできてません。  
　Eb(--gh) はsoftBV.exe \--gh　コマンドを使っています。BVPAとアルゴリズムが違うらしく，しばしば違う値が出ます。現状の調査では，私たちのEbの出し方に近いのはBVPAのほうのようです。(ちゃんと調査しなければいけないです)

### ボトルネックサイズ計算について

　ボトルネックの臨界イオン半径と三角形の面積は仮想原子Xを追加することで求めています。そのボトルネック位置入りのcifが新しいフォルダ\_ebi\_resultsに\_bnk.cifというcifとして吐き出されます。ただしpymatgenの仕様上，対称性が取り除かれています。P1です。  
　臨界イオン半径の求め方　参考に使ってる関数を載せてあります。:

1. 結晶構造をcifから読み取る pymatgen.core.structure.from\_file()   
2. 結晶構造から酸素を削除する　←この仕様により，現状酸化物イオン伝導体以外で臨界イオン半径を求めてるように見えてもデタラメになっています。  
3. ボトルネックの座標を呼び出し，その位置に仮想原子Xを置く  
4. 仮想原子Xから3 Å以内のカチオンを読み取る get\_neighbor()  
5. 近い3つのカチオンを呼び出す　←**この仕様により，ボトルネックが三角形でない場合や「広すぎる」場合も正しい値は出ません。その辺の判定ができたらいいのだが非常に難しい。ついでに四角形まで含めた臨界イオン半径を求めるのも難しそう。**  
6. それぞれのカチオンの配位数を自動で読み取る pymatgen.analysis.local\_env.VoronoiNN() ←実は配位数を出すアルゴリズムは2020年4月時点のpymatgenに少なくとも5種類あります。いくつか試してこれが私の感覚に近いので採用しました。論文に詳しく書くときもこれを使ってることを書いた方がいいかもしれません。  
   また，このアルゴリズムは酸素のdisorderをうまく取り扱ってくれないため，VoronoiNN()で読み取った酸素の占有率を足し合わせ，四捨五入するという形で実装しています。  
7. 酸化数を読み取る。酸化数が書いてないcifの場合，\_pop\_ox\_numbers.csvに書いてあるものを使う。  
8. 酸化数，配位数から対応するイオン半径を呼び出す。  
   また，disorderしている場合は平均のイオン半径を採用するようにしている。  
   **このときの平均のイオン半径は，占有率で重み付けしているのではなくすべてのイオンを等価に扱っています。実装が難しかったからこうしたけど割と不自然なので直したいところではある。 (1.2.0現在そのまま)**  
9. ニュートン法(藤井さんが作った臨界イオン半径計算スクリプトからそのまま移植)を用いて臨界イオン半径を算出。

書き出したイオン半径等の列の一番右は，藤井さんの臨界イオン半径計算にそのまま入れられるよう整形してあります。

## 更新予定メモ

全サドルのボトルネックを求めてもそんなに計算量増えないからやってもいいのかも？関数化してるから拡張も楽だし。記録のしかたを工夫すれば。  
配位数計算アルゴリズムのさらなる拡張。1.2.0時点ではEconNNを推奨しているが，最近出た文献  
Pan, H. et al. Benchmarking Coordination Number Prediction Algorithms on Inorganic Crystal Structures. doi:10.26434/chemrxiv.12508229.v1  
によると，CrystalNNがより推奨されるらしい。もっとも，EconNNやVoronoiNNもacceptable accuracyはもっていると結論に書いてある。  
それよりイオン半径の占有率による重み付けをはやく実装したいところではある。

1.2.0開発中  
内容

* 1.0.2で入れたのに1.0.3で抜けてしまった，構造解析したときの温度を記録する機能を再実装。いままでのoutputに影響を与えないように最後の列に書き出すようにした。  
* cifのリネーム部分を調節。名前被りでリネームできなかったとき拡張子が消えてしまうミスを修正  
* ボトルネックサイズ計算について，SoftBVと同様？「テストイオンを消してテストイオン以外は残す」ことにして，カチオン伝導でも少しはボトルネックの臨界イオン半径の結果が使えるようにした。  
  酸化物イオン以外にかんするテストは足りていないのでご協力をお願いします。  
* 配位数計算アルゴリズムを2種類から選べるようにした。VoronoiNN() のほか，EconNNはわりと知られているようだ (Hoppe, Rudolf. “Effective coordination numbers (ECoN) and mean fictive ionic radii (MEFIR).” Zeitschrift für Kristallographie-Crystalline Materials 150.1-4 (1979): 23-52.)  
* 鞍点の座標を書き出せるようにした  
* ボトルネックサイズの計算に失敗しても途中の座標を書き出せるようにした  
* ICSD ver2020.7 (4.4.0) の変更に(一部?)対応。  
  * 具体的には，空間群のcifにおける項目名が\_symmetry\_space\_group\_name\_H-Mから  
    \_space\_group\_name\_H-M\_alt  
    へ変わった。ただ，単純置換をしたらしく，後者の項目名かつR格子系の空間群では「R \-3 m H」と「R \-3 m R」に対応していないためSoftBVでエラーが出る。  
* そのため，R格子の最後のHとRは削除するようにした。単純削除でも，対象操作の項目\_space\_group\_symop\_operation\_xyzを併用するためとくに問題ないらしい。R格子とH格子それぞれで問題があったら報告をお願いします。
