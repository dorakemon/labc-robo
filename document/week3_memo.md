# 当日修正・確認・注意 事項

## パラメータ修正事項

- car_calibrator.pyで確認
  - [ ] **MOVE_VELOCITY**
  - [ ] **ROTATE_SOCOND**
  - [ ] **INIT_MOVE_TIME**

- [ ] **[CAMERA_X,CAMERA_Y]** カメラの中心座標のX,Yは今のままでいいか
  - カメラの画像の中でロボットのちょうど中心はどこか
  - 使用するカメラ(右左)で若干違う
  > image/getNearestLongLine, getAngle, getDistance  

- [ ] Mode.SEARCH時に判定面積をどうするか
  - 一部分判定面積
    - **MIX_PART_AREA** to **MAX_PART_AREA**
  - 全て映りの判定面積
    - **MIN_FULL_AREA** to **MAX_FULL_AREA**

- [ ] **SEARCH_MOVE_FORWARD_SEC**
  - 探索時に左右をカメラで見た後何秒間前進するか

- [ ] **CLOSE_D** どれくらい近くを狙って移動するか
  - 円全体を複数、誤検知なく見渡せるできるだけ近いが近すぎない距離
  > image/getBisectorPoint

- [ ] **HOUGH_PARA** ハフ変換パラメータ おそらく変える必要はない
  - Mode.AdjustAngleにして確認
  - CLOSE_Dの修正時にあまりにおかしければ修正
  > image/getHoughCircles

- [ ]  **ADJUST_ALLOW_PIXEL** 何ピクセルの横幅を許容するか
  - **CLOSE_D** によって横幅が変わる
  - **ADJUST_ANGLE** とともに修正
- > image/ADJUST_ALLOW_PIXEL

- [ ] **APPROACH_MOVE_SEC** APPROACH時に大体何秒間進んだら倒れるのか

## コード確認事項

- [ ] 赤・緑・青の紙を正しく認識するか
  - image/getMask()
- [ ] ハフ変換のためにカメラの角度をどうすればよいか
- [ ] controller.reverse()はちゃんと働くか
  - あまりに最初の地点と誤差が大きすぎなければよい

## コード注意事項

- もし画像バッファに溜まってしまうようであれば、*init_cam_count*を、毎度**0**に戻してあげる

- 探索時に予想より盤面が大きくて見つからなければ、~~(カメラを上げて)~~、移動を直線からジグザグとかがいいかも
  - この際に**MIN_PART_AREA**を修正する必要ある

- 探索時に盤面を超えてしまうことがある場合は、何回横向いたかを記録して、回数を記録してて、来た道を反転して戻るのがいいかも

- find_partialでserchに戻ってしまうときに、reverseするところが悪く働くかも
  - 一時的にループに入るようにしている
    - 前みる、右見る、左見る、少し進むを繰り返す
  - fp_stateにファイナル確認用の状態を作る
    - ひとつ前のfp_stateを持つべきかも
  - それぞれの状態で複数回確認する
  - init_cam_countを0ににしちゃう

- ANGLE_ADJUSTで円映ってる判定条件の ***len_circles > 2*** はよくないかも
  - CLOSE_Dとともに考える

- reverse時にmoveの反対がbackでもいいかどどうか

- 全体的にトルクは20 回転のペースは20にしているがそれで大丈夫か

- カメラ回り疎か

## 修正点

- reverse()がうまく働いていない

- **ANGLE_ADJUST** の首振ってなかなか終わらないことがある
  