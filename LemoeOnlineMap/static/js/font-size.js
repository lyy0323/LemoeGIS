
var html = document.documentElement; //获取到html元素
var hWidth = html.getBoundingClientRect().width;//获取到html的宽度
if(hWidth > 640) hWidth = 640; // 当hWidth大于640时，则物理分辨率大于1280（这就看设备的devicePixelRatio这个值了），应该去访问pc网站了
html.style.fontSize = hWidth/32 + "px"; //设置HTML的字体大小 font-size = 50px，1rem = 50px

