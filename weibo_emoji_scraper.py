# coding: utf-8

import sys
import re
import json
import argparse
import urlparse
import urllib2
import time
import os
import os.path
from weibo import APIClient

# emojis that Weibo has removed from the API response
LEGACY_EMOJIS = {
    '[打哈欠]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/f3/k_thumb.gif',
    '[呵呵]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/f3/k_thumb.gif',
    '[挖鼻屎]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/af/kl_org.gif',
    '[懒得理你]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/58/mb_org.gif',
    '[打哈气]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/9e/t_org.gif',
    '[睡觉]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7f/sleepya_org.gif',
    '[花心]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/40/cool_org.gif',
    '[不要]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/d8/good_org.gif',
    '[xb压力]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7e/ppbguzhang_org.gif',
    '[gst挖鼻屎]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/22/news_org.gif',
    '[gst舔舔]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/44/gstwabishi_org.gif',
    '[gst好羞射]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/83/gsttiantian_org.gif',
    '[gst抽你]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/8b/gsthaoxiushe_org.gif',
    '[gst好难懂]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/37/gstchouniya_org.gif',
    '[gst不活了]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/96/gsthaonandong_org.gif',
    '[gst转转转]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/3e/gstrangwosi_org.gif',
    '[gst汗]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ff/gstzhuanzhuanzhuan_org.gif',
    '[gst干嘛噜]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/2f/gsthan_org.gif',
    '[gst微博益起来]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ab/gstganmalu_org.gif',
    '[gst生日快乐]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/21/gstgongyi_org.gif',
    '[gst人家不依]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/f1/gstshengrikuaile_org.gif',
    '[gst热热热]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/1c/gstnewrenjiabuyi_org.gif',
    '[gst耐你]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/11/gstrerere_org.gif',
    '[gst困]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/1b/gstnaini_org.gif',
    '[gst好怕呀]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7c/gstkun_org.gif',
    '[gst发工资啦]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e5/gsthaopaya_org.gif',
    '[gst嘲笑你]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/41/gstfagongzila_org.gif',
    '[gst呀咩爹]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/d9/gstchaoxiaoni_org.gif',
    '[gst下班啦]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/09/gstyameidie_org.gif',
    '[gst晚安]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/73/gstxiabanla_org.gif',
    '[gst败了]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/8a/gstwanan_org.gif',
    '[gst死蚊子]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/35/gsttouxiang_org.gif',
    '[gst帅毙了]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/18/gstsiwenzi_org.gif',
    '[gst揉揉脸]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/fb/gstshuaibile_org.gif',
    '[gst嘿嘿嘿]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/52/gstrouroulian_org.gif',
    '[gst得瑟]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a0/gstheiheihei_org.gif',
    '[gst艾玛]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/14/gstdese_org.gif',
    '[xb自信]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/5b/longnianmtjj_org.gif',
    '[xb转]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/0a/xbzixin_org.gif',
    '[xb转圈]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/08/xbzhuan_org.gif',
    '[xb指指]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/fa/xbzhuanquan_org.gif',
    '[xb招手]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/fb/xbzhizhi_org.gif',
    '[xb照镜]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/69/xbzhaoshou_org.gif',
    '[xb雨]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/d7/xbzhaojing_org.gif',
    '[xb坏笑]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/c3/xbyu_org.gif',
    '[xb疑惑]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/49/xbyinxiao_org.gif',
    '[xb摇摆]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e9/xbyihuo_org.gif',
    '[xb眼镜]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/1d/xbyaobai_org.gif',
    '[xb星]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/6d/xbyanjing_org.gif',
    '[xb兴奋]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e8/xbxing_org.gif',
    '[xb喜欢]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7b/xbxingfen_org.gif',
    '[xb小花]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/5c/xbxihuan_org.gif',
    '[xb无奈]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/c2/xbxiaohua_org.gif',
    '[xb捂脸]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/96/xbwunai_org.gif',
    '[xb天使]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/56/xbwulian_org.gif',
    '[xb太阳]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/dc/xbtianshi_org.gif',
    '[xb睡觉]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/0f/xbtaiyang_org.gif',
    '[xb甩葱]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/af/xbshuijiao_org.gif',
    '[xb生日]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a2/xbshuaicong_org.gif',
    '[xb扇子]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/12/xbshengri_org.gif',
    '[xb伤心]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/41/xbshanzi_org.gif',
    '[xb揉]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/41/xbshangxin_org.gif',
    '[xb求神]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e1/xbrou_org.gif',
    '[xb青蛙]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a1/xbqiushen_org.gif',
    '[xb期待]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/06/xbqingwa_org.gif',
    '[xb泡澡]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/b0/xbqidai_org.gif',
    '[xb怒]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7a/xbpaozao_org.gif',
    '[xb努力]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/07/xbnu_org.gif',
    '[xb拇指]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7b/xbnuli_org.gif',
    '[xb喵]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/58/xbmuzhi_org.gif',
    '[xb喇叭]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/85/xbmiao_org.gif',
    '[xb哭]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/0c/xblaba_org.gif',
    '[xb看书]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/dd/xbku_org.gif',
    '[xb开餐]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/44/xbkanshu_org.gif',
    '[xb举手]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/34/xbkaican_org.gif',
    '[xb奸笑]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/8e/xbjushou_org.gif',
    '[xb昏]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/cf/xbjianxiao_org.gif',
    '[xb挥手]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/30/xbhun_org.gif',
    '[xb欢乐]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ec/xbhuishou_org.gif',
    '[xb喝茶]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/3a/xbhuanle_org.gif',
    '[xb汗]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/61/xbhecha_org.gif',
    '[xb害羞]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/36/xbhan_org.gif',
    '[xb害怕]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/cc/xbhaixiu_org.gif',
    '[xb风吹]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/c4/xbhaipa_org.gif',
    '[xb风车]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/66/xbfengchui_org.gif',
    '[xb恶魔]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a5/xbfengche_org.gif',
    '[xb打]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/28/xbemo_org.gif',
    '[xb大笑]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/72/xbda_org.gif',
    '[xb呆]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/cd/xbdaxiao_org.gif',
    '[xb触手]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/9d/xbdai_org.gif',
    '[xb吹]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/f4/xbchushou_org.gif',
    '[xb吃糖]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/0c/xbchui_org.gif',
    '[xb吃饭]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e9/xbchitang_org.gif',
    '[xb吃包]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/73/xbchifan_org.gif',
    '[xb唱歌]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/48/xbchibao_org.gif',
    '[xb摆手]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/1c/xbchangge_org.gif',
    '[cai走走]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/db/xbbaishou_org.gif',
    '[cai揍人]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/6a/caizouzou_org.gif',
    '[cai撞墙]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/25/caizouren_org.gif',
    '[cai正呀]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/54/caizhuangqiang_org.gif',
    '[cai嘻嘻]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/68/caizhengya_org.gif',
    '[cai羞羞]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/fc/caixixi_org.gif',
    '[cai无语]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7f/caixiuxiu_org.gif',
    '[cai脱光]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/6f/caiwuyu_org.gif',
    '[cai偷摸]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/53/caituoguang_org.gif',
    '[cai太好了]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/c8/caitoutoumomo_org.gif',
    '[cai庆祝]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/41/caitaihaole_org.gif',
    '[cai钱]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/b0/caiqingzhu_org.gif',
    '[cai潜水]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/91/caiqian_org.gif',
    '[cai怕羞]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/70/caiqianshui_org.gif',
    '[cai落叶]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/6a/caipaxiu_org.gif',
    '[cai哭]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/40/cailuoye_org.gif',
    '[cai开心]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/90/caiku_org.gif',
    '[cai惊吓]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e2/caikaixin_org.gif',
    '[cai奸笑]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a9/caijingxia_org.gif',
    '[cai晃头]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/63/caijianxiao_org.gif',
    '[cai哈喽]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/22/caihuangtou_org.gif',
    '[cai飞吻]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/dc/caihalou_org.gif',
    '[cai肚腩]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/75/caifeiwen_org.gif',
    '[cai打打]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/07/caidunan_org.gif',
    '[cai扯脸]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/1d/caidada_org.gif',
    '[cai插眼]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/95/caichelian_org.gif',
    '[cai鼻屎]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/97/caichayan_org.gif',
    '[cai崩溃]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/21/caibishi_org.gif',
    '[cai拜拜]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a7/caibengkui_org.gif',
    '[cai啊]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a4/caibaibai_org.gif',
    '[lb装傻]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/60/caia_org.gif',
    '[lb咦]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/5e/lbzhuangsha_org.gif',
    '[lb嗯]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/07/lbyi_org.gif',
    '[lb糟糕]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/fe/lben_org.gif',
    '[lb嘿嘿]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/3c/lbzaogao_org.gif',
    '[lb鄙视]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/df/lbheihei_org.gif',
    '[lb戳]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a7/lbbishi_org.gif',
    '[lb摇头]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7b/lbchuo_org.gif',
    '[lb惊]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/65/lbyaotou_org.gif',
    '[lb欢乐]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/68/lbjing_org.gif',
    '[lb雷]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/19/lbhuanle_org.gif',
    '[lb呃]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/fe/lblei_org.gif',
    '[lb蹭右]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e9/lbe_org.gif',
    '[lb蹭左]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/c8/lbcengyou_org.gif',
    '[lb啊]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/27/lbcengzuo_org.gif',
    '[lb哼]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/98/lba_org.gif',
    '[lb撒欢]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ea/lbheng_org.gif',
    '[lb爽]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7a/lbsahuan_org.gif',
    '[lb味]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/dc/lbshuang_org.gif',
    '[lb厉害]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/d1/lbwei_org.gif',
    '[lb帅]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/bf/lblihai_org.gif',
    '[lb哭]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/0d/lbshuai_org.gif',
    '[lb呵]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ec/lbku_org.gif',
    '[lb嘻]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/9b/lbhe_org.gif',
    '[lb讨厌]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/12/lbxi_org.gif',
    '[ala晕]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/5a/lbtaoyan_org.gif',
    '[ala郁闷]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/87/alayun_org.gif',
    '[ala耶]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ee/alayumen_org.gif',
    '[ala羞]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/10/alaye_org.gif',
    '[ala舔舔]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/99/alaxiu_org.gif',
    '[ala泪汪汪]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/5a/alatiantian_org.gif',
    '[ala加油]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ea/alaleiwangwang_org.gif',
    '[ala飞吻]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/d4/alajiayou_org.gif',
    '[ala得意]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/6c/alafeiwen_org.gif',
    '[ala搓搓]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/09/aladeyi_org.gif',
    '[ala蹦]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/28/alacuocuo_org.gif',
    '[ala杯具]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/b7/alabeng_org.gif',
    '[ala爱国]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/51/alabeiju_org.gif',
    '[ala扭啊扭]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/54/alaaichina_org.gif',
    '[ala吐舌头]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/8f/altniuaniu_org.gif',
    '[ala么么]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/3a/alttushetou_org.gif',
    '[ala嘿嘿嘿]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ac/altmeme_org.gif',
    '[ala哼]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/94/altheiheihei_org.gif',
    '[ala囧]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/cc/altheng_org.gif',
    '[ala上火]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/b3/altjiong_org.gif',
    '[ala啊哈哈哈]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/1b/altshanghuo_org.gif',
    '[ala飘走]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/6a/altahahaha_org.gif',
    '[ala吃货]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/33/altpiaozou_org.gif',
    '[ala悲催]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a5/altchihuo_org.gif',
    '[ala讨厌]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/f2/altbeicui_org.gif',
    '[ala衰]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/43/alttaoyan_org.gif',
    '[alt拜年]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7c/altshuai_org.gif',
    '[甜馨得瑟]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ea/bbhltianxindese_org.gif',
    '[甜馨翻白眼]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/83/bbhltxfanbaiyan_org.gif',
    '[甜馨颜值高]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e4/bbhlyanzhigao_org.gif',
    '[甜馨尴尬]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ce/bbhltianxingg_org.gif',
    '[甜馨热热]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/dd/bbhltianxihot_org.gif',
    '[甜馨爱你哟]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ea/bbhltianxinlove_org.gif',
    '[甜馨哭哭]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/bc/bbhltianxinkk_org.gif',
    '[求抱抱]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/f1/bbhlqiubaobao_org.gif',
    '[甜馨不想长大]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/47/bbhltianxinbuxiangzhangda_org.gif',
    '[甜馨吃货]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/ec/bbhlchihuo_org.gif',
    '[我想静静]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/e5/bbhlwoxiangjingjing_org.gif',
    '[萌神奥莉]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/d6/bbhlaolims_org.gif',
    '[羞羞哒甜馨]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/a9/bbhltianxinxxd_org.gif',
    '[歪果仁夏克立]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/9c/bbqnxiakeli_org.gif',
    '[xkl扭]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/25/xklniu_org.gif',
    '[xkl你拍一]': 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/da/xklnipaiyi_org.gif',
}
WEIBO_EMOJI_WEBROOT = 'http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/'

parser = argparse.ArgumentParser(description='Generate Weibo emoji JSON and download emojis')
parser.add_argument('-k', '--key', dest='api_key', type=str, required=True,
                    help='Weibo API Key')
parser.add_argument('-s', '--secret', dest='api_secret', type=str, required=True,
                    help='Weibo API Secret')
parser.add_argument('-t', '--token', dest='api_token', type=str, required=True, help='Weibo API Token')
parser.add_argument('--emojitypes', dest='emoji_types', type=str, default='cartoon,ani,face', 
                    help='Weibo emoji categories, csv, e.g. cartoon,ani,face')
parser.add_argument('--destfolder', dest='output_folder', type=str, default='emojis',
                    help='Destination folder to save emojis')
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug messages.')
parser.add_argument('--simulate', action='store_true',
                    help='Run simulation only, no files saved or generated.')

args = parser.parse_args()

client = APIClient(app_key=args.api_key, app_secret=args.api_secret,
                   redirect_uri='')
client.set_access_token(args.api_token, int(time.time() + 60 * 60 * 24))

latest_emojis = {}
all_emojis = {}
for phrase, img_url in LEGACY_EMOJIS.items():
    all_emojis[phrase] = img_url

for emoji_type in [emoji_type.strip() for emoji_type in args.emoji_types.split(',')]:
    emojis = client.emotions.get(type=emoji_type)
    for emoji in emojis:
        if not emoji['url'].endswith('.gif'):
            # skip non-gif emojis, usually swf
            continue
        phrase = emoji['phrase']
        all_emojis[phrase] = emoji['url']
        latest_emojis[phrase] = emoji['url']

    if args.debug:
        with open('%s.debug.json' % emoji_type, 'wb') as debug_output:
            debug_output.write(json.dumps(emojis, indent=4, separators=(',', ': ')))

print '%d total emojis from API.' % len(latest_emojis)
print '%d total emojis generated.' % len(all_emojis)

# Generate json with Weibo full image paths
if args.debug:
    print 'Generating weibo_emojis.full.json...'
if not args.simulate:
    with open('weibo_emojis.full.json', 'wb') as output:
        output.write(json.dumps(all_emojis, indent=4, separators=(',', ': ')))

# Generate json with Weibo full image paths - minified
if args.debug:
    print 'Generating weibo_emojis.full.min.json...'
if not args.simulate:
    with open('weibo_emojis.full.min.json','wb') as output:
        output.write(json.dumps(all_emojis))

# Generate json with Weibo full image paths - without legacy emojis
if args.debug:
    print 'Generating weibo_emojis.nolegacy.full.json...'
if not args.simulate:
    with open('weibo_emojis.nolegacy.full.json','wb') as output:
        output.write(json.dumps(latest_emojis, indent=4, separators=(',', ': ')))

# Generate json with Weibo full image paths - without legacy emojis - minified
if args.debug:
    print 'Generating weibo_emojis.nolegacy.full.min.json...'
if not args.simulate:
    with open('weibo_emojis.nolegacy.full.min.json','wb') as output:
        output.write(json.dumps(latest_emojis))

# Update master list of emojis
if args.debug:
    print 'Updating Master List master.json...'
with open('master.json') as master_file:
    master_list = json.load(master_file)
for phase, img_url in latest_emojis.items():
    master_list[phrase] = img_url
if not args.simulate:
    with open('master.json','wb') as output:
        output.write(json.dumps(master_list, indent=4, separators=(',', ': ')))
print '%d total emojis in master.' % len(master_list)

# Check if emojis in master is missing from all_emojis
for phrase, img_url in master_list.items():
    if phrase not in all_emojis and phrase.encode('utf-8') not in all_emojis:
        print 'MISSING: ', phrase, img_url

for phrase, img_url in all_emojis.items():
    if args.debug:
        print phrase + '\t' + img_url
    if img_url.startswith(WEIBO_EMOJI_WEBROOT):
        filename = img_url.replace(WEIBO_EMOJI_WEBROOT, '')
    else:
        filename = urlparse.urlparse(img_url).path[1:]
    
    # to catch img urls like http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/c8/../e0/hongbao1_org.gif
    filename = re.sub(r'[^/]+/\.\./', '', filename)
    output_filename = os.path.join(args.output_folder, filename)

    # create folder if necessary
    try:
        if not args.simulate:
            if not os.path.exists(os.path.dirname(output_filename)):
                os.makedirs(os.path.dirname(output_filename))

            if not os.path.isfile(output_filename):
                # download if file does not exist
                request = urllib2.Request(img_url, headers={'User-agent': 'Mozilla/5.0'})
                contents = urllib2.urlopen(request).read()
                with open(output_filename,'wb') as output:
                    output.write(contents)

        if img_url.startswith(WEIBO_EMOJI_WEBROOT):
            img_url = img_url.replace(WEIBO_EMOJI_WEBROOT, '')
        else:
            img_url = re.sub('http://ww[0-9]+.sinaimg.cn/', '', img_url)
        all_emojis[phrase] = re.sub(r'[^/]+/\.\./', '', img_url)    # relative paths

    except Exception as e:
        print 'ERROR for ', phrase + '\t' + img_url
        raise e

# Generate json with relative paths
if args.debug:
    print 'Generating weibo_emojis.relative.json...'
if not args.simulate:
    with open('weibo_emojis.relative.json','wb') as output:
        output.write(json.dumps(all_emojis, indent=4, separators=(',', ': ')))

# Generate json with relative paths - minified
if args.debug:
    print 'Generating weibo_emojis.relative.min.json...'
if not args.simulate:
    with open('weibo_emojis.relative.min.json','wb') as output:
        output.write(json.dumps(all_emojis))
