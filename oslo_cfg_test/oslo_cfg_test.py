# -_-coding:utf-8-_-
from oslo.config import cfg
import sys

conf = cfg.CONF

# ####命令行##########
comand_opts = [
    cfg.StrOpt(name="country", default="china", metavar="CN",help="the place person born")
]
conf.register_cli_opts(comand_opts)
######End#############

conf(sys.argv[1:])
default_opts = [
    cfg.StrOpt(name="name", default="caesar"),
    cfg.IntOpt(name="age", default="18")
]
conf.register_opts(default_opts)

print("my name is :%s and age is %s" %(conf.name, conf.age))

print("my country is %s" % conf.country)
