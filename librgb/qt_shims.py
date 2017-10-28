# pylint: disable=unused-import

try:
    from PyQt5 import QtCore
    from PyQt5 import QtGui
    from PyQt5 import QtWidgets

except ImportError:
    try:
        from PySide import QtCore
        from PySide import QtGui
    except ImportError:
        from PyQt4 import QtCore
        from PyQt4 import QtGui

    QtWidgets = QtGui
