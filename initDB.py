#coding=utf-8
#
#

from app import db
from app.models import User, Role

password_str = '-' \
               'JhyVJFVg9wdQNkzMdVbduMRWrJVkhsETkUnAqxVvvyNtoo2yi6zXQwpcJjHoegmbMNPEyQfXtYCKE3ajKasjYRsnhbMQqwRb' \
                'MIIGJDCCBQygAwIBAgISAzJ7YvIMb4e0zFmkQbt70fHcMA0GCSqGSIb3DQEBCwUAMEoxCzAJBgNVBAYTAlVTMRYwFAYDVQQK' \
                'Ew1MZXQncyBFbmNyeXB0MSMwIQYDVQQDExpMZXQncy0IEF1dGhvcml0eSBYMzAeFw0xODA0MTYwMzIzNDVaFw0xODA3MTUwM' \
                'zIzNDVaMB4xHDAaBgNVBAMMEyouY2hpbmFjbG91ZC5jb20uY24wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC5Z' \
                'qA+lPkP9fzq65vtJGt55OeygbA1yEfRg25REjbSR7mLfQppqsUFtEwtWV8TvNWhs3JwXqjnBY15EYvxOXLgrMnosLX7wIfPW' \
                'K4HKlyuiZ1IAdHCUlFUlvvUy5bNsmCrhxTOf86rbq3nOnxST2XHq6PAegdtCUaMj/7ilooc93wj6uOicBCgCIkeG6udi11HH' \
                'HfiJAoRpR5XFR9YO35OJQhJENhuYpbN/05fHdBV7vv+T9fnrDQw7enwPPZkRpMyhda3MzbQ1s5HghGuTIhJ8hdSDwitXe3RM' \
                'J9PmLOAtD67MsKezAi0Bcy4HQhlS+o7bIwWuk2FcnPBUdbmZzl5AgMBAAGjggMuMIIDKjAOB'

role_str = {
    'super': 0,         # 超级用户
    'admin': 1,         # 公司管理层
    'manager': 2,       # 部门负责人
    'pd_manager': 3,    # 产品负责人
    'pj_manager': 4,    # 项目负责人
    'sys_manager': 66,  # 系统维护人
    'user': 99,         # 一般用户
}

email_str = {
    'chairman@chinacloud.com.cn': 'super',
    'zhuhongtao@chinacloud.com.cn': 'admin',
    'lijiacheng@chinacloud.com.cn': 'admin',
    'nieyong@chinacloud.com.cn': 'admin',
    'wuhuaigu@chinacloud.com.cn': 'admin',
    'minshengjie@chinacloud.com.cn': 'admin',
    'dingxing@chinacloud.com.cn': 'manager',
    'guanyuqi@chinacloud.com.cn': 'manager',
    'shishuang@chinacloud.com.cn': 'manager',
    'hongbo@chinacloud.com.cn': 'manager',
    'gaijia@chinacloud.com.cn': 'manager',
    'jiangyong@chinacloud.com.cn': 'manager',
    'guofengqi@chinacloud.com.cn': 'manager',
    'liuyi@chinacloud.com.cn': 'manager',
    'zhangjian@chinacloud.com.cn': 'manager',
    'yangfei@chinacloud.com.cn': 'manager',
    'lianguo@chinacloud.com.cn': 'manager',
    'zhangjing@chinacloud.com.cn': 'manager',
    'lixia@chinacloud.com.cn': 'manager',
    'liyating@chinacloud.com.cn': 'manager',
    'wuyuming@chinacloud.com.cn': 'manager',
    'xuwenbao@chinacloud.com.cn': 'pd_manager',
    'wangxuekai@chinacloud.com.cn': 'pd_manager',
    'cuihaozhi@chinacloud.com.cn': 'pd_manager',
    'raodingyuan@chinacloud.com.cn': 'pd_manager',
    'duhao@chinacloud.com.cn': 'pj_manager',
    'dongjingyi@chinacloud.com.cn': 'pj_manager',
    'dengliujiang@chinacloud.com.cn': 'pj_manager',
    'wangli@chinacloud.com.cn': 'pj_manager',
    'masong@chinacloud.com.cn': 'pj_manager',
    'liuqiang@chinacloud.com.cn': 'pj_manager',
    'liujinlong@chinacloud.com.cn': 'pj_manager',
    'tianlong@chinacloud.com.cn': 'pj_manager',
    'jiayangzheng@chinacloud.com.cn': 'pj_manager',
    'guohaipeng@chinacloud.cm.cn': 'pj_manager',
    'wangyunfeng@chinacloud.com.cn': 'pj_manager',
    'xietao@chinacloud.com.cn': 'pj_manager',
    'liuxiaokun@chinacloud.com.cn': 'pj_manager',
    'marui@chinacloud.com.cn': 'pj_manager',
    'wujing@chinacloud.com.cn': 'pj_manager',
    'zhufeng@chinacloud.com.cn': 'pj_manager',
    'huaicuijing@chinacloud.com.cn': 'user',
    'liangkangli@chinacloud.com.cn': 'user',
    'weilihong@chinacloud.com.cn': 'user',
    'xiabing@chinacloud.com.cn': 'user',
    'baiyin@chinacloud.com.cn': 'user',
    'caiyali@chinacloud.com.cn': 'user',
    'chengyu@chinacloud.com.cn': 'user',
    'chenyanqiu@chinacloud.com.cn': 'user',
    'guanjiuwei@chinacloud.com.cn': 'user',
    'heyuyang@chinacloud.com.cn': 'user',
    'huzhengbo@chinacloud.com.cn': 'user',
    'jiaguangyuan@chinacloud.com.cn': 'user',
    'jinyi@chinacloud.com.cn': 'user',
    'liangyu@chinacloud.com.cn': 'user',
    'lichengbang@chinacloud.com.cn': 'user',
    'lichenge@chinacloud.com.cn': 'user',
    'linwengang@chinacloud.com.cn': 'user',
    'liubingying@chinacloud.com.cn': 'user',
    'qinliyi@chinacloud.com.cn': 'user',
    'qiushi@chinacloud.com.cn': 'user',
    'renchao@chinacloud.com.cn': 'user',
    'tanglei@chinacloud.com.cn': 'user',
    'tanglina@chinacloud.com.cn': 'user',
    'wangdinghua@chinacloud.com.cn': 'user',
    'wangkun@chinacloud.com.cn': 'user',
    'wangwei@chinacloud.com.cn': 'user',
    'wangxu@chinacloud.com.cn': 'user',
    'wangyihua@chinacloud.com.cn': 'user',
    'wangyu@chinacloud.com.cn': 'user',
    'xiaweihu@chinacloud.com.cn': 'user',
    'xulang@chinacloud.com.cn': 'user',
    'yangkairui@chinacloud.com.cn': 'user',
    'yangzhilin@chinacloud.com.cn': 'user',
    'yutao@chinacloud.com.cn': 'user',
    'zhaming@chinacloud.com.cn': 'user',
    'zhanjinwei@chinacloud.com.cn': 'user',
    'zhangyirui@chinacloud.com.cn': 'user',
    'zhangyuandong@chinacloud.com.cn': 'user',
    'zhangzhixian@chinacloud.com.cn': 'user',
    'zhengbiao@chinacloud.com.cn': 'user',
    'zhoulun@chinacloud.com.cn': 'user',
    'zhuguoqing@chinacloud.com.cn': 'user',
    'tongxiaoyu@chinacloud.com.cn': 'user',
    'liji@chinacloud.com.cn': 'user',
    'caojingyi@chinacloud.com.cn': 'user',
    'fangbo@chinacloud.com.cn': 'user',
    'gechao@chinacloud.com.cn': 'user',
    'jinwei@chinacloud.com.cn': 'user',
    'lijia@chinacloud.com.cn': 'user',
    'lili@chinacloud.com.cn': 'user',
    'lilinhong@chinacloud.com.cn': 'user',
    'lishichinacloud.com.cn': 'user',
    'liubo@chinacloud.com.cn': 'user',
    'longchaoguo@chinacloud.com.cn': 'user',
    'longjungang@chinacloud.com.cn': 'user',
    'mamengyun@chinacloud.com.cn': 'user',
    'qiyang@chinacloud.com.cn': 'user',
    'wangmingxia@chinacloud.com.cn': 'user',
    'wangyizhi@chinacloud.com.cn': 'user',
    'wangyuhong@chinacloud.com.cn': 'user',
    'weizhuo@chinacloud.com.cn': 'user',
    'wengwei@chinacloud.com.cn': 'user',
    'xiakai@chinacloud.com.cn': 'user',
    'xiemeizhong@chinacloud.com.cn': 'user',
    'yangqinzi@chinacloud.com.cn': 'user',
    'yuyuehong@chinacloud.com.cn': 'user',
    'zengqia@chinacloud.com.cn': 'user',
    'zhangxin@chinacloud.com.cn': 'user',
    'wanghaoyong@chinacloud.com.cn': 'user',
    'zhongtao@chinacloud.com.cn': 'user',
    'jinhao@chinacloud.com.cn': 'user',
    'kangqingwei@chinacloud.com.cn': 'user',
    'liyong@chinacloud.com.cn': 'user',
    'xuliang@chinacloud.com.cn': 'user',
    'zhangjiaqi@chinacloud.com.cn': 'user',
    'chenwei@chinacloud.com.cn': 'user',
    'leishiran@chinacloud.com.cn': 'user',
    'lihelin@chinacloud.com.cn': 'user',
    'liuhang@chinacloud.com.cn': 'user',
    'lixin@chinacloud.com.cn': 'user',
    'wangdaojin@chinacloud.com.cn': 'user',
    'wangzhong@chinacloud.com.cn': 'user',
    'zhangzijian@chinacloud.com.cn': 'user',
    'zhaoxiaoming@chinacloud.com.cn': 'user',
    'dengleilei@chinacloud.com.cn': 'user',
    'liugaoyang@chinacloud.com.cn': 'user',
    'longqian@chinacloud.com.cn': 'user',
    'yuanfeng@chinacloud.com.cn': 'user',
    'baoxiaoyu@chinacloud.com.cn': 'user',
    'chenchuan@chinacloud.com.cn': 'user',
    'duanjinming@chinacloud.com.cn': 'user',
    'wangqiang@chinacloud.com.cn': 'user',
    'yexingceng@chinacloud.com.cn': 'user',
    'zhugaojun@chinacloud.com.cn': 'user',
    'guoziming@chinacloud.com.cn': 'user',
    'zhaohailong@chinacloud.com.cn': 'user',
    'chenhongying@chinacloud.com.cn': 'user',
    'dinglinmin@chinacloud.com.cn': 'user',
    'guchenchen@chinacloud.com.cn': 'user',
    'sunyuhua@chinacloud.com.cn': 'user',
    'yangming@chinacloud.com.cn': 'user',
    'zengjun@chinacloud.com.cn': 'user',
    'zhongquanmei@chinacloud.com.cn': 'user',
    'dingfan@chinacloud.com.cn': 'user',
    'dongyizhou@chinacloud.com.cn': 'user',
    'douguofeng@chinacloud.com.cn': 'user',
    'fususheng@chinacloud.com.cn': 'user',
    'guijia@chinacloud.com.cn': 'user',
    'hujianbin@chinacloud.com.cn': 'user',
    'leilei@chinacloud.com.cn': 'user',
    'liuweiping@chinacloud.com.cn': 'user',
    'liuxiaoxiong@chinacloud.com.cn': 'user',
    'liuyichun@chinacloud.com.cn': 'user',
    'menghongyang@chinacloud.com.cn': 'user',
    'shenguo@chinacloud.com.cn': 'user',
    'sunshasha@chinacloud.com.cn': 'user',
    'sunyu@chinacloud.com.cn': 'user',
    'tonghao@chinacloud.com.cn': 'user',
    'xiaoqingshan@chinacloud.com.cn': 'user',
    'xuyayang@chinacloud.com.cn': 'user',
    'baili@chinacloud.com.cn': 'user',
    'shijiahao@chinacloud.com.cn': 'user',
    'limin@chinacloud.com.cn': 'user',
    'qihong@chinacloud.com.cn': 'user',
    'tanggaofei@chinacloud.com.cn': 'user',
    'caopan@chinacloud.com.cn': 'user',
    'chenxia@chinacloud.com.cn': 'user',
    'lihaiyan@chinacloud.com.cn': 'user',
    'lihongxia@chinacloud.com.cn': 'user',
    'pengzhi@chinacloud.com.cn': 'user',
    'qinxing@chinacloud.com.cn': 'user',
    'sunbanghui@chinacloud.com.cn': 'user',
    'tanyingqing@chinacloud.com.cn': 'user',
    'tianxin@chinacloud.com.cn': 'user',
    'wanghui@chinacloud.com.cn': 'user',
    'wudanyang@chinacloud.com.cn': 'user',
    'xiangxiaoyan@chinacloud.com.cn': 'user',
    'zhangzhiying@chinacloud.com.cn': 'user',
    'chenzhenzhu@chinacloud.com.cn': 'user',
    'doujiayu@chinacloud.com.cn': 'user',
    'fushuxiang@chinacloud.com.cn': 'user',
    'gaozhenqing@chinacloud.com.cn': 'user',
    'hejinlong@chinacloud.com.cn': 'user',
    'jianghui@chinacloud.com.cn': 'user',
    'liangyanlong@chinacloud.com.cn': 'user',
    'liling@chinacloud.com.cn': 'user',
    'liujiawei@chinacloud.com.cn': 'user',
    'liuyuxing@chinacloud.com.cn': 'user',
    'tangcheng@chinacloud.com.cn': 'user',
    'tangyong@chinacloud.com.cn': 'user',
    'wangxuemin@chinacloud.com.cn': 'user',
    'wangzhe@chinacloud.com.cn': 'user',
    'xuzhou@chinacloud.com.cn': 'user',
    'yinqiang@chinacloud.com.cn': 'user',
    'zhuqiang@chinacloud.com.cn': 'user',
    'baile@chinacloud.com.cn': 'user',
    'bianyue@chinacloud.com.cn': 'user',
    'cuifu@chinacloud.com.cn': 'user',
    'chanhaiyang@chinacloud.com.cn': 'user',
    'dongxujun@chinacloud.com.cn': 'user',
    'fujinwan@chinacloud.com.cn': 'user',
    'liujunlei@chinacloud.com.cn': 'user',
    'liumuchen@chinacloud.com.cn': 'user',
    'luguoqiang@chinacloud.com.cn': 'user',
    'lvchunlei@chinacloud.com.cn': 'user',
    'pangyunfei@chinacloud.com.cn': 'user',
    'wangxin@chinacloud.com.cn': 'user',
    'wangyuanyuan@chinacloud.com.cn': 'user',
    'xuebingqian@chinacloud.com.cn': 'user',
    'yuanlei@chinacloud.com.cn': 'user',
    'zhangjialong@chinacloud.com.cn': 'user',
    'zhangshaolin@chinacloud.com.cn': 'user',
    'zhangyin@chinacloud.com.cn': 'user',
    'zhangzhen@chinacloud.com.cn': 'user',
    'baojing@chinacloud.com.cn': 'user',
    'chenhuilie@chinacloud.com.cn': 'user',
    'chenjing@chinacloud.com.cn': 'user',
    'dongjuanjuan@chinacloud.com.cn': 'user',
    'guchunxue@chinacloud.com.cn': 'user',
    'mazhenyu@chinacloud.com.cn': 'user',
    'tangxiaoxiao@chinacloud.com.cn': 'user',
    'xulan@chinacloud.com.cn': 'user',
    'zhangjing_cd@chinacloud.com.cn': 'user',
    'zhaoyibei@chinacloud.com.cn': 'user',
}


def init_users():

    import random

    pwd_str_len = len(password_str)
    print pwd_str_len

    for _email in email_str:

        _idx = random.randint(1, pwd_str_len-12)
        _password = str(password_str[_idx:_idx+8])

        # db.session.query(User).filter_by(email=_email).delete(synchronize_session=False)
        # db.session.commit()
        user = User.query.filter_by(email=_email).first()
        if user is None:

            user = User()
            user.username = _email
            user.email = _email

            if email_str[_email] == 'user':
                _password = '12345678'

            user.password = _password
            db.session.add(user)
            db.session.commit()

            # db.session.query(Role).filter_by(name=_email).delete(synchronize_session=False)
            # db.session.commit()

            role = Role()
            role.name = _email
            role.level = role_str[email_str[_email]]
            role.secretkey = '20131226'
            db.session.add(role)
            db.session.commit()

            print(">>> user: %s , password: %s" % (_email, _password))

