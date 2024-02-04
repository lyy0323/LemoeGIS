from typing import Union


def rtx(rgb: tuple) -> str:
    """Converts RGB color to HEX color.

    Args:
        rgb: color expressed in RGB.

    Returns:
        A string of color expressed in HEX form, which can be recognized by CSS. Example: '#66ccff'
    """
    return '#' + ('%02x%02x%02x' % rgb)


def xtr(x: str) -> tuple:
    """Converts HEX color to RGB color.

    Args:
        x: color expressed in 6-digit HEX, either or not startswith '#'. Example: '#66CCFF', '66CCFF', '66ccff'

    Returns:
        A tuple of color expressed in RGB form. Example: (102, 204, 255)
    """
    x = x.strip('#')
    return tuple(int(x[i: i + 2], 16) for i in range(0, 6, 2))


def avg(*colors: Union[str, tuple]):
    """
    Gives an average of all input colors.

    Note: this is not simply numerical average.

    Args:
        colors: a series of colors. Either in HEX or RGB form.

    Returns:
        A tuple of color expressed in RGB form. Example: (102, 204, 255)
    """
    color_list = []
    for clr in colors:
        if str(clr).startswith('#'):
            clr = clr.strip('#')
            color_list.append(tuple(int(clr[i:i + 2], 16) for i in range(0, 6, 2)))
        elif type(clr) == tuple:
            color_list.append(clr)
    d0 = sum([sum([_[i] ** 2 for i in range(3)]) for _ in color_list]) / len(color_list)
    c0 = [sum(_[i] for _ in color_list) / len(color_list) for i in range(3)]
    k = (d0 / max(0.01, sum(c0[_] ** 2 for _ in range(3)))) ** 0.5
    avg_clr = [min(255, int(k * c0[_])) for _ in range(3)]
    return tuple(avg_clr)


def clgrad(n, cl1, cl2):
    color_list = []
    for i in range(n):
        cls = [cl1] * (n - i - 1) + [cl2] * i
        color_list.append(avg(*cls))

    def ex(x=None):
        if x:
            return list(map(rtx, color_list))
        else:
            return color_list

    return ex


def simplegrad(cl):
    def ex(x=None):
        if x:
            return clgrad(8, '#333333', cl)(1)[:-1] + clgrad(8, cl, '#CCCCCC')(1)
        else:
            return clgrad(8, '#333333', cl)()[:-1] + clgrad(8, cl, '#CCCCCC')()

    return ex


def dualgrad(cl1, cl2):
    def ex(x=None):
        if x:
            return clgrad(6, '#000000', cl1)(1)[:-1] + clgrad(5, cl1, cl2)(1)[:-1] + clgrad(6, cl2, '#FFFFFF')(1)
        else:
            return clgrad(6, '#000000', cl1)()[:-1] + clgrad(5, cl1, cl2)()[:-1] + clgrad(6, cl2, '#FFFFFF')()

    return ex


def softdualgrad(cl1, cl2):
    def ex(x=None):
        if x:
            return (clgrad(6, '#FFFFFF', cl1)(1)[:-1] + clgrad(6, cl1, cl2)(1)[:-1] + clgrad(6, cl2, '#FFFFFF')(1))[
                   3: 13]
        else:
            return (clgrad(6, '#FFFFFF', cl1)()[:-1] + clgrad(6, cl1, cl2)()[:-1] + clgrad(6, cl2, '#FFFFFF')())[3: 13]
    return ex


def isDeep(cl):
    if type(cl) == str:
        cl = xtr(cl)
    if cl[1] < 51:
        return True
    elif cl[1] > 204:
        return False
    else:
        if (sum(list(map(lambda x: x ** 2, cl))) / 3) ** 0.5 < 160:
            return 1
        else:
            return 0


if __name__ == '__main__':
    print(rtx((176, 33, 38)))
    print(xtr("#B02E26"))
    print(avg('#66CCFF', (112, 48, 160)))
    print(clgrad(6, (0, 0, 0), '#33CC33')())
    print(simplegrad('#3AB3DA')(1))
    print(dualgrad((176, 46, 38), '#3C44AA')())
    print(softdualgrad((176, 46, 38), '#3C44AA')())
