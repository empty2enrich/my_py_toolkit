# my_py_toolkit
 Some common methods written or found in inetrnet by myself of python.

# The useage:

下载源码并进入根目录：
```
git clone https://github.com/emptyknowledge/my_py_toolkit.git
cd my_py_toolkit
```

源码安装方式一：
```
python setup.py sdist
cd dist
pip install <package_name>
```
源码安装方式二：

```
# 打开 git bash: Windows 不能直接运行 sh 文件，使用 git sh 运行
# 使用 env_name 指定虚拟环境, 不指定使用默认环境安装 （window 下有问题，可以不指定）
# window 环境下 sh 执行有点问题，执行步骤：
#   1、安装 git, 并把 bin 文件夹添加到环境变量
#   2、打开 anaconda prompt 激活虚拟环境，然后执行脚本
./setup.sh env_name
```
