# 4週目確認事項等

## 修正事項

- [ ] FIND_PARTIALの処理を大きく修正

- [ ] 角度調整時のハフ変換のwhile loopの抜け方

## 実験前に

- [ ] ★*car_calibrator.py*で**reverse()**の動作確認を入念に行う
  - reverse()は誤差が大きすぎるのと無駄な挙動が多すぎてなくした
  
- [ ] **FINDPART_MOVE_FORWARD_SEC**のパラメータを修正
- [ ] あるモードでループに入り込んでしまう場合はclassにupdateカウントを取り入れる

- init cam count と imread loop のカウント

- 紙なしでSESRCH2の挙動

## 後で

SEARCH -> init
SEARCH2 -> SEARCH
