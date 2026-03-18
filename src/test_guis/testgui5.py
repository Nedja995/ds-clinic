import tkinter as tk
import inspect
class Class:
    '''クラスを描画するためのクラス'''
    CLASS_COUNTER = 0
    def __init__(self, canvas, name):
        self.canvas = canvas
        self.name = name
        self.start_pos = None
        self.connections = []
        Class.CLASS_COUNTER += 1
        x = 150 + 200 * (Class.CLASS_COUNTER % 5)
        y = 150 + 50 * (Class.CLASS_COUNTER // 5)
        text = canvas.create_text(x, y, text=name, tag=name)
        rect = canvas.create_rectangle(canvas.bbox(name), tag=name, fill="lightyellow")
        canvas.tag_lower(rect, text)
        canvas.tag_bind(name, "<ButtonPress>", self.start)
        canvas.tag_bind(name, "<Motion>", self.move)
        canvas.tag_bind(name, "<ButtonRelease>", self.end)
    def start(self, event):
        '''クラスをクリックされたときのメソッド'''
        self.start_pos = (self.canvas.canvasx(event.x),
                          self.canvas.canvasy(event.y))
    def move(self, event):
        '''クラスを動かすためのメソッド'''
        if self.start_pos is None:
            return
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        dx, dy = x - self.start_pos[0], y - self.start_pos[1]
        self.canvas.move(self.name, dx, dy)
        self.start_pos = x, y
        for connection in self.connections:
            connection.move(self)
    def end(self, event):  # pylint: disable=unused-argument
        '''クラスの選択が終わった時のメソッド'''
        self.start_pos = None
    def get_center(self):
        '''中心点を戻す'''
        bbox = self.canvas.bbox(self.name)
        return (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
    @property
    def x(self):
        '''左上のx座標を戻す'''
        bbox = self.canvas.bbox(self.name)
        return bbox[0]
    @property
    def y(self):
        '''左上のy座標を戻す'''
        bbox = self.canvas.bbox(self.name)
        return bbox[1]
    @property
    def height(self):
        '''高さを戻す'''
        bbox = self.canvas.bbox(self.name)
        return abs(bbox[1] - bbox[3])
    @property
    def width(self):
        '''幅を戻す'''
        bbox = self.canvas.bbox(self.name)
        return abs(bbox[0] - bbox[2])
    def add_listener(self, connection):
        ''' コネクションのリスナーを登録します '''
        self.connections.append(connection)
class Inheritance:
    '''継承関係の線を表示するためのクラス'''
    def __init__(self, canvas, parent, child):
        self.canvas = canvas
        self.parent = parent
        self.child = child
        parent.add_listener(self)
        child.add_listener(self)
        p_coords = self.get_intersection(parent)
        c_coords = self.get_intersection(child)
        self.id = self.canvas.create_line(*p_coords, *c_coords, arrow=tk.FIRST)
    def get_intersection(self, box):
        ''' 矩形との接点を求める '''
        x, y = box.get_center()
        height, width = box.height // 2, box.width // 2
        dx, dy = self.child.x - self.parent.x, self.child.y - self.parent.y
        if box == self.child:
            dx, dy = -dx, -dy
        if dx == 0:
            dx = 0.001
        if abs(dy / dx) < (height / width):  # 垂直側
            x_pos = x + width if dx > 0 else x - width
            y_pos = y + dy * width / abs(dx)
        else:  # 水平側
            x_pos = x + dx * height / abs(dy)
            y_pos = y + height if dy > 0 else y - height
        return x_pos, y_pos
    def move(self, box):
        ''' エンティティが移動したときの処理（エンティティから呼び出される）'''
        coords = self.canvas.coords(self.id)
        if box == self.parent:
            coords[0:2] = self.get_intersection(box)
            coords[2:4] = self.get_intersection(self.child)
        elif box == self.child:
            coords[0:2] = self.get_intersection(self.parent)
            coords[2:4] = self.get_intersection(box)
        self.canvas.coords(self.id, coords)
class Application:
    '''アプリケーションクラス'''
    def __init__(self, root):
        self.root = root
        root.title("tkinter classes")
        root.geometry("1200x800")
        self.start_pos = None
        self.item = None
        self.canvas = tk.Canvas(root, background="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Motion>", self.move)
        self.classes = {}
        self.init()
    def init(self):
        '''初期化'''
        for name, obj in inspect.getmembers(tk):
            if inspect.isclass(obj):
                if name in ('getdouble', 'getint', '_setit'):
                    continue
                if name not in self.classes.keys():
                    self.classes[name] = Class(self.canvas, name)
                for parent in obj.__bases__:
                    p_name = parent.__name__
                    if p_name == 'object':
                        continue
                    if p_name not in self.classes.keys():
                        self.classes[p_name] = Class(self.canvas, p_name)
                    print(p_name, "<--", name)
                    Inheritance(self.canvas, self.classes[p_name], self.classes[name])
    def move(self, event):
        '''マウスが動いたときにタイトルに座標を表示します'''
        title = "tkinter class[" + str(event.x) + "," + str(event.y) + "]"
        self.root.title(title)
def main():
    '''主処理'''
    root = tk.Tk()
    application = Application(root)
    application.root.mainloop()
if __name__ == "__main__":
    main()