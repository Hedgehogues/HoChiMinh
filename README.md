# Ho Chi Minh

## Overview

Ho Chi Minh is designed to extract textual information from tables presented in PDF, pictures or other format.
If the table is strongly tilted, the data will not be extracted correctly. PDF is transformed into pictures (page by page),
and then each image is processed separately.

The utility ignores the text layer and treats any pdf as a picture.

It is assumed that on one page there is exactly one table, which is not transferred to the next page. If
on the page there are several tables, then most likely the recognition will be incorrect.

Ho Chi Minh City does not know how to work with complex tables, in which several cells are united together:

![Complex table](data/README/clever_table.png)

Then, in the majority of cases, simple tables are correctly recognized:

![Simple table](data/README/simple_table.png) 

If the table occupies only a small part of the image or does not have
obvious boundaries, then it probably will not be is recognized.

Ho Chi Minh allows to get the frame of the table in the form of a list of cells, each of which is represented by four points
(cell angles). Cell is a class:

    class Cell:
        def __init__(self, x_min=0, x_max=0, y_min=0, y_max=0, prob=0.0, text=''):
            # Coordinates of the cell in the picture
            self.x_min = x_min
            self.x_max = x_max
            self.y_min = y_min
            self.y_max = y_max

            # Probability of correct extraction of cell coordinates
            self.prob = prob
            # Text inside the cell
            self.text = text

To extract the text, you can use the following code:

    templator = TableRecognizer(
            reader=ImageFromPDFReader(
                PDFConverter(in_path=path + 'pdf/', out_path=path + 'pdf/images/', resolution=130)
            ),
            hough_transformer=SobelDirector(),
            connected_components=ConnectedComponents(),
            cross_detector=CrossDetector(max_steps=15, detected_steps=8, line_width=8),
            ocr=TesseractWrapper(),
            binarization=210
        )
        table = []
        for i in range(4):
            table.append(templator.next_points())

## Algorithm

The principle of operation of the algorithm can be described with the help of the following scheme:

![Flowchart](data/README/block_scheme.png)

* Reader. Reading the next picture from the pool using the reader.
* Detector of Horisontal and vertical lines. The image shows the most obvious and long horizontal and vertical lines.

![Исходное изображение](data/README/etalon_image.png)
![Вертикальные границы](data/README/horisontal_edge.png)
![Горизонтальные границы](data/README/vertical_edge.png)

For each line, its coordinate is memorized (for horizontal lines - $ y $, for vertical ones - $ x $). Then, all 
possible pairs of points $ (x, y) $ are constructed. All of them are candidates for the corners of the cells of the
 table.
 
![Точки-кандидаты](data/README/detected_points.png)

* Detector the largest connected components. We select the largest (we consider the area of ​​the rectangle in which it
is) a connected component. All candidate points that belong to it are left, we forget about the others.

* Detect cross of table. Some of the points highlighted in the table render superfluous. Some of them lie not at the intersection
parties, and in an arbitrary place on the side of the table. All extra points are deleted.

![Selected points](data/README/connected_components_points.png)

* Uniques points. As a result of the operation performed in the previous step, only those points that lie in the nodes remain
tables. In this case, in some nodes there are more than 1 point. This stage is aimed at obtaining a single point in each
node.

* Building table. The table is constructed. In connection with the fact that part of the node points $ (x, y) $ may not be
is recognized, we construct a table as the Cartesian product of the set $\{x\}\times\{y\} $. In this case, if some cells
tables were unified, then there is an erroneous recognition.

![Table](data/README/table.png)

* OCR. Each cell is considered separately. Recognition is carried out.


# Хошимин

## Обзор

Хошимин предназначен для извлечения текстовой информации из таблиц, представленных в PDF, картинках или ином формате.
Если таблица сильно наклонена, то данные извлекутся некорректно. PDF предварительно преобразуется в картинки (постранично),
а затем каждое изображение обрабатывается отдельно.

Утилита игнорирует текстовый слой и рассматривает любой pdf как картинку.

Предполагается, что на одной странице существует ровно одна таблица, которая не переносится на следующую страницу. Если
на странице существует несколько таблиц, то вероятнее всего распознование произойдёт некорректно.

Хошимин не умеет работать со сложными таблицами, в которых несколько ячеек объеденены воедино:

![Сложная таблица](data/README/clever_table.png)

При этом, в большинстве случае корректно распознаются простые таблицы:

![Простая таблица](data/README/simple_table.png)

Если таблица занимает лишь небольшую часть изображения или же не имеет явных границ, то, вероятно, она не будет
распознана.

Хошимин позволяет получить каркас таблицы в виде списка ячеек, каждая из которых представлена четырьмя точеками
(углы ячейки). Ячейка (Cell) представляет собой класс:

    class Cell:
        def __init__(self, x_min=0, x_max=0, y_min=0, y_max=0, prob=0.0, text=''):
            # Координаты ячейки на картинке
            self.x_min = x_min
            self.x_max = x_max
            self.y_min = y_min
            self.y_max = y_max

            # Вероятность корректного извлечения координат ячейки
            self.prob = prob
            # Текст внутри ячейки
            self.text = text

Для извлечения текстовой можно воспользоваться следующим кодом:

    templator = TableRecognizer(
        reader=ImageFromPDFReader(
            PDFConverter(in_path=path + 'pdf/', out_path=path + 'pdf/images/', resolution=130)
        ),
        hough_transformer=SobelDirector(),
        connected_components=ConnectedComponents(),
        cross_detector=CrossDetector(max_steps=15, detected_steps=8, line_width=8),
        ocr=TesseractWrapper(),
        binarization=210
    )
    table = []
    for i in range(4):
        table.append(templator.next_points())

## Алгоритм

Принцип работы алгоритма можно описать при помощи следующей схемы:

![Блок-схема](data/README/block_scheme.png)

* Reader. Прочтение очередной картинки из пула при помощи ридера.

* Detector of Horisontal and vertical lines. На изображении выделяются наиболее явные и протяжённые горизонтальные и
вертикальные линии.

![Исходное изображение](data/README/etalon_image.png)
![Вертикальные границы](data/README/horisontal_edge.png)
![Горизонтальные границы](data/README/vertical_edge.png)

Для каждой линии запоминается её координата (для горизонтальных - $y$, для вертикальных - $x$). Затем,
строятся все возможные пары точек $(x, y)$. Все они являются кандидатами для углов ячеек таблицы.

![Точки-кандидаты](data/README/detected_points.png)

* Detector the largest connected components. Выделяем самую большую (считаем площадь прямоугольника, в котором она
находится) связную компоненту. Все точки-кандидаты, пренадлежащие ей, оставляем, про остальные забываем.

* Detect cross of table. Часть точек, выделенных в таблице оказывает излишними. Некоторые из них лежат не на пересечении
сторон, а в произвольном месте на стороне таблицы. На все лишние точки удаляются.

![Отобранные точки](data/README/connected_components_points.png)

* Uniques points. В результате проведённой операции на предыдущем шаге, остаются лишь те точки, которые лежат в узлах
таблицы. При этом, в некоторых узлах лежит более 1 точки. Данный этап направлен на получение единственной точки в каждом
узле.

* Building table. Производится построение таблицы. В связи с тем, что часть узловых точек $(x, y)$ может быть не
распознано, построим таблицу, как декартово произведение множества $\{x\} \times \{y\}$. При этом, если некоторые ячейки
таблицы были объеденены, то возникает ошибочное распознование.

![Таблица](data/README/table.png)

* OCR. Рассматривает каждая, отдельно взятая ячейка. Производится распознование.
