if [ $1 ] ; then
echo "选择虚拟环境: $1 "
rm -rf dist/* && activate $1 && python setup.py sdist && cd dist && pip install * && rm -rf *
else
echo "未选择虚拟环境，选择默认环境安装"
rm -rf dist/* && python setup.py sdist && cd dist && pip install * && rm -rf * 
fi
