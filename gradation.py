# -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets, QtSql

class GradationWidget(QtWidgets.QWidget):
    def __init__(self):
        super(GradationWidget, self).__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.setWindowTitle('gradation')

        self.resize(500, 55)

        self.scene = Scene()
        self.scene.setObjectName('Scene')
        self.scene.setSceneRect(0, 0, 500, 50)
        self.view = QtWidgets.QGraphicsView(self.scene, self)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.view)

        _ls = [
            [0.0, QtCore.Qt.white],
            [1.0, QtCore.Qt.black]
        ]
        for _l in _ls:
            _c = ColorNode(_l[0], _l[1])
            self.scene.add_item(_c)
            _c.set_pos_from_ratio()
            _c.moving.connect(self.scene.update)


class Scene(QtWidgets.QGraphicsScene):

    @property
    def width(self):
        return self.sceneRect().width()

    @property
    def height(self):
        return self.sceneRect().height()

    @property
    def gradation_width(self):
        return self.sceneRect().width() - self.margin * 2

    def __init__(self):
        super(Scene, self).__init__()
        # memo
        # 大量のitemを追加した際、addItemだけ使っているとitemが消失する不具合があったので
        # 自分でも保持しておく
        self.add_items = []
        self.margin = 8
        self.gradation_height = 25

    def drawBackground(self, painter, rect):

        grad1 = QtGui.QLinearGradient(self.margin, 0, self.width - self.margin * 2, self.gradation_height)
        for c in self.add_items:
            grad1.setColorAt(c.ratio, c.color)
        painter.setBrush(QtGui.QBrush(grad1))
        painter.drawRect(self.margin, 0, self.width - self.margin * 2, self.gradation_height)

    def mouseDoubleClickEvent(self, event):
        ratio = self.get_pos_to_ratio(event.scenePos())
        _c = ColorNode(ratio, QtCore.Qt.darkGray)
        self.add_item(_c)
        _c.set_pos_from_ratio()
        _c.moving.connect(self.update)
        self.update()

    def add_item(self, widget):
        if not isinstance(widget, list):
            widget = [widget]
        for _w in widget:
            self.add_items.append(_w)
            self.addItem(_w)

    def remove_item(self, widget):
        if not isinstance(widget, list):
            widget = [widget]
        for _w in widget:
            self.add_items.remove(_w)
            self.removeItem(_w)

    def clear(self):
        for _i in self.items():
            self.remove_item(_i)
        self.add_items = []

    def get_pos_to_ratio(self, pos):
        ratio = pos.x() / (self.width - self.margin)
        if ratio < 0:
            ratio = 0
        elif ratio > 1:
            ratio = 1
        return ratio


class ColorNode(QtWidgets.QGraphicsObject):
    DEF_Z_VALUE = 0.1
    moving = QtCore.Signal()

    @property
    def rect(self):
        return QtCore.QRect(0, 0, self.width, self.height)

    def set_pos_from_ratio(self):
        self.setX(self.scene().gradation_width * self.ratio + self.scene().margin)
        self.setY(self.scene().gradation_height + 5)

    def __init__(self, ratio=0.0, color=None):

        self.ratio = ratio

        super(ColorNode, self).__init__()
        self.setZValue(self.DEF_Z_VALUE)
        self.width = 10
        self.height = 10
        if color is None:
            self.color = QtGui.QColor(60, 60, 60, 255)
        else:
            self.color = color

        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setRotation(45)

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(0, 255, 255, 255))

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        self.brush.setColor(self.color)
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRoundedRect(self.rect, 0, 0)

    def mouseMoveEvent(self, event):
        self.moving.emit()
        super(ColorNode, self).mouseMoveEvent(event)
        self.ratio = self.scene().get_pos_to_ratio(self.pos())
        self.set_pos_from_ratio()

    def mouseReleaseEvent(self, event):
        super(ColorNode, self).mouseReleaseEvent(event)

        # マウスのボタンを離した際にシーンから一定距離離れていたら色情報削除
        pos = event.scenePos()
        _del_margin = 30
        if any([pos.x() < 0 - _del_margin, pos.x() > self.scene().width + _del_margin, pos.y() < 0 - _del_margin,
                pos.y() > self.scene().height + _del_margin]):
            s = self.scene()
            self.delete()
            s.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            color = QtWidgets.QColorDialog.getColor(self.color)
            if not color.isValid():
                return
            self.color = color
            self.update()
            self.scene().update()
        super(ColorNode, self).mousePressEvent(event)

    def delete(self):
        self.scene().remove_item(self)


def main():
    import sys
    app = QtWidgets.QApplication.instance()
    w = GradationWidget()
    w.show()
    app.exec_()
    sys.exit()


if __name__ == '__main__':
    main()
# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
