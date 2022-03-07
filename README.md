# Character Identifier

A Python program that can identify handwritten characters A, B, C, and 1 via a manually implemented Computer Vision prototype.

## How to Run

The code can be run by simply double-clicking the file. Please note that only Windows users can run this program.

## Dependencies

The code installs its dependencies by checking the installed packages every time it runs, but in case of an error, here is the list:

1. [Pillow](https://pypi.org/project/Pillow/)
2. [NumPy](https://pypi.org/project/numpy/)
3. [PySimpleGUI](https://pypi.org/project/PySimpleGUI/)

## Algorithm

Algorithm has a total of 7 steps:

1. Alpha Channel Cleanup
2. Grayscale
3. Binarization
4. Labeling
5. Getting Coordinates
6. Identifying
7. Generating Output

The pictures of the test run is done with default values.

### Raw Demo Picture

<p align="center">
<img width="400" src=https://user-images.githubusercontent.com/66966617/157057237-bd7369e4-a83c-4dff-8025-9e71d3912843.png>
</p>

Note: The "Alpha Channel" text on the picture is a transparency which is on alpha channel. The test run is done with default values which are 220 for the threshold and 8-Connected for the labeling type.

### 1. Alpha Channel Cleanup

If the picture has alpha (transparency) channel, the algorithm paints the transparent pixels and deletes the channel. 

<p align="center">
<img width="400" src=https://user-images.githubusercontent.com/66966617/157057727-63c65229-fe41-417f-b15d-4e2e7101c23d.png>
</p>

### 2. Grayscale

The picture is converted to grayscale in order to apply the binarization. The demo picture is already in black and white, so the output is the same.

<p align="center">
<img width="400" src=https://user-images.githubusercontent.com/66966617/157058087-c67faa3e-253d-401d-9e1d-a2f814fd63ee.png>
</p>

### 3. Binarizaiton

Each pixel of the picture is binarized by the given threshold. If the value of the pixel is below the threshold, it is 0 which is represented by black. Otherwise, it is 1 which is represented by white.

<p align="center">
<img width="400" src=https://user-images.githubusercontent.com/66966617/157058611-8fe4dbcc-d826-4d98-aaa4-db695d65849a.png>
</p>

### 4. Labeling

The pixels are checked if they are connected with each other. The connection method is given by the user under the "Labeling Type" option. If the method is 4-Connected, then only 4 neighbour pixels are checked for being connected, but if the method is 8-Connected, all the pixels around the current pixel are checked. The connected pixels are painted with the same color. (Credits: [@muhittingokmen](https://github.com/muhittingokmen))

<p align="center">
<img width="400" src=https://user-images.githubusercontent.com/66966617/157059613-a0baa39f-645f-45bb-86f0-519b52c285a0.png>
</p>

### 5. Getting Coordinates

For each label, a loop, which runs 4 times, goes from the first row of the picture to the last row to find the current label. If the loop finds the label in a row, it rotates the picture and continues to the next iteration. After 4 iterations, the coordinates of corners for that label are found.

<p align="center">
<img width="400" src=https://user-images.githubusercontent.com/66966617/157060775-50d0e9a1-864d-4f8d-abab-6bd91bb1f88e.png>
</p>

### 6. Identifying

A loop goes through all labels to cut the image in pieces, so that every piece is used for checking only one character. In each iteration, the cut piece is again enters to the labeling process, but this time, the binarized values are flipped. After the labelization process, the label count is used for identifying the character. If the count is 3, this means the character is B, and if it is 2, the character is A. Seperating C and 1 is more complicated because their label count is both 1. A special algorithm is implemented to seperate them. The success rate of this algorithm is approximately 90%.

<p align="center">
<img width="400" src=https://user-images.githubusercontent.com/66966617/157062386-f88e4c21-58ef-46e2-ad05-ac295fd725a2.png>
</p>


--- WILL CONTINUE ---








