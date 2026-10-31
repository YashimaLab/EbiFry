# 全酸化物の BVE スクリーニング

softBVを利用した活性化障壁計算プログラム(改良型)とスクリーニング結果

**作成日**: 2026年4月14日  
**更新日**: 2026年10月31日  
**作成者**: 益山  

## 1. 概要
2026年4月14日現在ICSDに登録されている **129158件すべての酸化物について、BVE スクリーニングを行った。**  
計算は`EbiFry_v3.py`としてラッピングされたsoftBVによって行われた。

計算時点におけるすべてのsoftBVを利用した酸化物イオン伝導体スクリーニングは完了しているため、原則その計算結果である、`BVE_screening_Eb.csv` を参照すれば良い。  
csvファイルの使い方は次章「2.`BVE_screening_Eb.csv` の使い方」を、データ構造の詳細は `BVE_screening_Eb_csv_Description.md` を参照すること。

もし `EbiFry_v3.py` で新規に登録された結晶構造に対してスクリーニングを行ったり、プログラムを改造したりする場合はプログラムをAIに解析させて良い。

`EbiFry_v3.py` のもととなった `ebi.py` の技術仕様に関しては `Ebi_py_Manual.md` を参照すること。

## 2. `BVE_screening_Eb.csv` の使い方
基本的にはスクリーニングしたい対象 CIF ファイルのチートシートとして機能する。

1. ICSDで対象としたい結晶構造群を検索し、すべてのICSD ID を列挙する。
2. それらを python で読み取り、「BVE_screening_Eb.csv」 pythonでDataFrame として読み込む。
3. スクリーニング対象のICSD ID を 「BVE_screening_Eb.csv」 から作った DataFrameと照合し、それらの活性化障壁の情報を引き出す。
4. 結果をCSVファイルなどに出力させて確認。

データ照合プログラムの作成から始めても、30分ほどで全手順が終わるはず。慣れていればどんなに CIF ファイルが多くとも10分で行えるだろう。

## 3. このスクリプトや計算結果を利用したものを論文にするとき
このスクリプトは以下の外部プログラム要素を含んでいるため，それらの論文を引用するとともに，それらのソフトのライセンスも一読すること。  
学会発表でもどこかに記載しておくほうがよいと思われる。

softBV-command line version: [http\://www\.dmse.nus.edu.sg/asn/softBVCL.html](http://www.dmse.nus.edu.sg/asn/softBVCL.html)    
H. Chen, L.L. Wong, S.Adams; SoftBV \- a software tool for screening the materials genome of inorganic fast ion conductors. *Acta Crystallogr.* B 75 (2019), 18-33. [https\://doi.org/10.1107/S2052520618015718](https://doi.org/10.1107/S2052520618015718) (as the source of the code)  
H. Chen, S. Adams; Bond softness sensitive bond-valence parameters for crystal structure plausibility tests. *IUCrJ* 4 (2017) 614-625. [https\://doi.org/10.1107/S2052520618015718](https://doi.org/10.1107/S2052520618015718)  (as the source of the BV parameters)

Pymatgen [https\://pymatgen.org/index.html\#](https://pymatgen.org/index.html#)   
P. Ong, W. D. Richards, A. Jain, G. Hautier, M. Kocher, S. Cholia, D. Gunter, V. L. Chevrier, K. A. Persson and G. Ceder, Python Materials Genomics (pymatgen): A robust, open-source python library for materials analysis, *Comput. Mater. Sci.*, 2013, 68, 314–319.  
10.1016/j.commatsci.2012.10.028

## 4. おわりに
本データベースを作るための計算は多数の方の協力によって遂行されました。心より感謝いたします。

**協力**: 平川・関根・濱田・今岡・宇田川
