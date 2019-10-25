#include <stdio.h>
#include <math.h>
#include <stdlib.h>

typedef struct Pair {
    double first, second;
} Pair;

double sigmoid(double x, double mean, double var, double shift, double p) {
    return 1. / (1 + exp(-pow(abs(var * x - mean), p))) - shift;
}

Pair varians_mean(unsigned char *x, int count) {
    double mean = 0;
    double var = 0;
    for (int i = 0; i < count; ++i) {
        mean += x[i] / 255.;
    }
    mean = mean / (double) count;
    double mean_square = pow(mean, 2);
    for (int i = 0; i < count; ++i) {
        double val = x[i] / 255.;
        var += (val * val - mean_square);
    }
    var = var / (double) count;
    var = sqrt(var);

    Pair answ;
    answ.first = mean;
    answ.second = var;
    return answ;
}

//function [d, m] = GetParams(img, area)
//    %img2=img
//    %imshow(img2)
//    %imshow(subimg)
//
//    for x = (1 + area) : (size(img, 2) - area)
//        for y = (1 + area) : (size(img, 1) -  area)
//            subimg = img((y - area) : (y + area), (x - area) : (x + area) );
//            subimg = GetApprox(subimg);
//            %imshow(subimg)
//%             if (x == 437 && y == 49)
//%                 figure(20);
//%                 hist(subimg(:), 12);
//%             end
//            m(y, x) = sum(double(subimg(:) ) .^ 1.1) / numel(subimg);
//            d(y, x) = sum(abs((double(subimg(:) ) - m(y, x) ) ) .^ 2);
//        end
//    end
//end
//
//function newimg = GetApprox(img, count)
//    newimg = [];
//    for y = 1 : (size(img, 1) - 1)
//        for x = 1 : (size(img, 2) - 1)
//            newimg(end + 1) = img(y, x);
//            for index = 1 : count
//                xVal = rand(1);
//                yVal = rand(1);
//                newimg(end + 1) = [1 - xVal xVal] * [img(y, x), img(y + 1, x); img(y, x + 1) img(y + 1, x + 1)] * [1 - yVal; yVal];
//            end
//        end
//    end
//end

void get_sub_matrix(const unsigned char *image, int y, int x, int row_count, int col_count, unsigned char border,
                    unsigned char *submatrix, int *count) {
    int step = 0;
    for (int i = y - border; i < y + border + 1; ++i) {
        if ((i >= row_count) || (i < 0)) {
            continue;
        }
        for (int j = x - border; j < x + border + 1; ++j) {
            if ((j >= col_count) || (j < 0)) {
                continue;
            }
            submatrix[step] = image[i * col_count + j];
            ++step;
        }
    }
    *count = step;
}

void cfun(const void *image, int row_count, int col_count, unsigned char border, double mean_pow, double var_pow, double shift, double p, void *prepared_image) {
    unsigned char *submatrix = malloc((2 * border + 1) * (2 * border + 1) * sizeof(unsigned char));
    const unsigned char *image_ = (unsigned char *) image;
    double *prepared_image_ = (double *) prepared_image;

    for (int i = 0; i < row_count; ++i) {
        for (int j = 0; j < col_count; ++j) {
            int count = 0;
            get_sub_matrix(image_, i, j, row_count, col_count, border, submatrix, &count);
            Pair answ = varians_mean(submatrix, count);
            double mean = answ.first;
            double var = answ.second;
            prepared_image_[i * col_count + j] = sigmoid(image_[i * col_count + j], pow(mean, mean_pow), pow(var, var_pow), shift, p);
        }
    }
    free(submatrix);
}
//
//int main() {
//    unsigned char image[8][9];
//    double p_image[8][9];
//    unsigned char border = 1;
//    double mean_pow = 1;
//    double var_pow = 1;
//
//    for(int j = 0; j < 8; j++){
//        for(int i = 0; i < 9; i++) {
//            image[j][i] = (unsigned char) (rand() % 256);
//        }
//    }
//
//    cfun(image, 8, 9, border, mean_pow, var_pow, p_image);
//    return 0;
//}