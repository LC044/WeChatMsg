# 说明

## 解析
```shell
protoc --decode_raw < msg_data.txt
```

## 根据解析结果，设置.proto文件
```shell
1 {
  1: 16
  2: 0
}
3 {
  1: 1
  2: "wxid_4b1t09d63spw22"
}
3 {
  1: 7
  2: "<msgsource>\n\t<alnode>\n\t\t<fr>2</fr>\n\t</alnode>\n\t<sec_msg_node>\n\t\t<uuid>c6680ab2c57499a1a22e44a7eada76e8_</uuid>\n\t</sec_msg_node>\n\t<silence>1</silence>\n\t<membercount>198</membercount>\n\t<signature>v1_Gj7hfmi5</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n"
}
3 {
  1: 2
  2: "c13acbc95512d1a59bb686d684fd64d8"
}
3 {
  1: 4
  2: "yiluoAK_47\\FileStorage\\Cache\\2023-08\\2286b5852db82f6cbd9c2084ccd52358"
}
```
## 生成python文件
```shell
protoc --python_out=. msg.proto
```