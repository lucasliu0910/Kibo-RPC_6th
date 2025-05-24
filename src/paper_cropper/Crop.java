public class Crop extends KiboService {
    public Mat crop(Mat input, String area) {
        Mat undistortedImg = undistort(input);

        Mat grayImg = new Mat();
        if (undistortedImg.channels() > 1) {
            Imgproc.cvtColor(undistortedImg, grayImg, Imgproc.COLOR_BGR2GRAY);
        } else {
            undistortedImg.copyTo(grayImg);
        }

        Mat ids = new Mat();
        List<Mat> corners = new ArrayList<>();
        List<Mat> rejected = new ArrayList<>();

        DetectorParameters detectorParams = DetectorParameters.create();
        detectorParams.set_minMarkerPerimeterRate(detector_para.get(area)[0]);
        detectorParams.set_maxMarkerPerimeterRate(detector_para.get(area)[1]);

        Aruco.detectMarkers(grayImg, ar_dictionary, corners, ids, detectorParams, rejected);

        int targetId = area_tag_id.get(area);
        boolean foundTargetMarker = false;
        int markerIndex = -1;

        if (ids.total() > 0) {
            for (int i = 0; i < ids.total(); ++i) {
                int id = (int) ids.get(i, 0)[0];
                if (id == targetId) {
                    markerIndex = i;
                    foundTargetMarker = true;
                    break;
                }
            }
        }

        if (foundTargetMarker) {
            Mat corner = corners.get(markerIndex);

            double[] topLeft = corner.get(0, 0);
            double[] topRight = corner.get(0, 1);
            double[] bottomRight = corner.get(0, 2);
            double[] bottomLeft = corner.get(0, 3);

            double paperWidthRatio = 27.0 / 4.5;
            double paperHeightRatio = 15.0 / 4.5;

            double[] xVec = {topRight[0] - topLeft[0], topRight[1] - topLeft[1]};
            double[] yVec = {bottomLeft[0] - topLeft[0], bottomLeft[1] - topLeft[1]};

            double xVecLength = Math.sqrt(xVec[0] * xVec[0] + xVec[1] * xVec[1]);
            double yVecLength = Math.sqrt(yVec[0] * yVec[0] + yVec[1] * yVec[1]);

            double[] xVecNorm = {xVec[0] / xVecLength, xVec[1] / xVecLength};
            double[] yVecNorm = {yVec[0] / yVecLength, yVec[1] / yVecLength};

            double tagToPaperLeftDistance = 20.0 + 2.25;
            double tagToPaperTopDistance = 3.75;

            double markerCenterX = (topLeft[0] + topRight[0] + bottomRight[0] + bottomLeft[0]) / 4;
            double markerCenterY = (topLeft[1] + topRight[1] + bottomRight[1] + bottomLeft[1]) / 4;

            double markerSize = (xVecLength + yVecLength) / 2;

            double scale = markerSize / 4.5;

            double[] paperTopLeft = new double[2];
            double[] paperTopRight = new double[2];
            double[] paperBottomLeft = new double[2];
            double[] paperBottomRight = new double[2];

            paperTopLeft[0] = markerCenterX - tagToPaperLeftDistance * scale * xVecNorm[0] - tagToPaperTopDistance * scale * yVecNorm[0];
            paperTopLeft[1] = markerCenterY - tagToPaperLeftDistance * scale * xVecNorm[1] - tagToPaperTopDistance * scale * yVecNorm[1];

            paperTopRight[0] = paperTopLeft[0] + paperWidthRatio * markerSize * xVecNorm[0];
            paperTopRight[1] = paperTopLeft[1] + paperWidthRatio * markerSize * xVecNorm[1];

            paperBottomLeft[0] = paperTopLeft[0] + paperHeightRatio * markerSize * yVecNorm[0];
            paperBottomLeft[1] = paperTopLeft[1] + paperHeightRatio * markerSize * yVecNorm[1];

            paperBottomRight[0] = paperTopRight[0] + paperHeightRatio * markerSize * yVecNorm[0];
            paperBottomRight[1] = paperTopRight[1] + paperHeightRatio * markerSize * yVecNorm[1];

            double minX = Math.min(Math.min(paperTopLeft[0], paperTopRight[0]),
                    Math.min(paperBottomLeft[0], paperBottomRight[0]));
            double maxX = Math.max(Math.max(paperTopLeft[0], paperTopRight[0]),
                    Math.max(paperBottomLeft[0], paperBottomRight[0]));
            double minY = Math.min(Math.min(paperTopLeft[1], paperTopRight[1]),
                    Math.min(paperBottomLeft[1], paperBottomRight[1]));
            double maxY = Math.max(Math.max(paperTopLeft[1], paperTopRight[1]),
                    Math.max(paperBottomLeft[1], paperBottomRight[1]));

            int startX = Math.max(0, (int)Math.floor(minX));
            int startY = Math.max(0, (int)Math.floor(minY));
            int endX = Math.min(grayImg.width() - 1, (int)Math.ceil(maxX));
            int endY = Math.min(grayImg.height() - 1, (int)Math.ceil(maxY));

            int width = endX - startX;
            int height = endY - startY;

            if (width <= 0 || height <= 0) {
                Log.e("xString", "Unable to calculate cropping area, use default. Area: " + area);

                int imgWidth = grayImg.width();
                int imgHeight = grayImg.height();

                width = (int)(imgWidth * 0.8);
                height = (int)(width * 15.0 / 27.0);

                startX = (int)(imgWidth * 0.1);
                startY = (imgHeight - height) / 2;
            }

            Rect cropRect = new Rect(startX, startY, width, height);
            Mat croppedImg = new Mat(grayImg, cropRect);

            if (crop_img_counter < 10) {
                Mat debugImg = undistortedImg.clone();
                if (debugImg.channels() == 1) {
                    Imgproc.cvtColor(debugImg, debugImg, Imgproc.COLOR_GRAY2BGR);
                }

                Imgproc.circle(debugImg, new Point(topLeft[0], topLeft[1]), 5, new Scalar(255, 0, 0), 2);
                Imgproc.circle(debugImg, new Point(topRight[0], topRight[1]), 5, new Scalar(0, 255, 0), 2);
                Imgproc.circle(debugImg, new Point(bottomRight[0], bottomRight[1]), 5, new Scalar(0, 0, 255), 2);
                Imgproc.circle(debugImg, new Point(bottomLeft[0], bottomLeft[1]), 5, new Scalar(255, 255, 0), 2);

                Imgproc.circle(debugImg, new Point(paperTopLeft[0], paperTopLeft[1]), 8, new Scalar(255, 0, 255), 2);
                Imgproc.circle(debugImg, new Point(paperTopRight[0], paperTopRight[1]), 8, new Scalar(255, 0, 255), 2);
                Imgproc.circle(debugImg, new Point(paperBottomRight[0], paperBottomRight[1]), 8, new Scalar(255, 0, 255), 2);
                Imgproc.circle(debugImg, new Point(paperBottomLeft[0], paperBottomLeft[1]), 8, new Scalar(255, 0, 255), 2);

                Imgproc.rectangle(debugImg, new Point(startX, startY), new Point(endX, endY), new Scalar(0, 255, 255), 2);

                api.saveMatImage(debugImg, "paper_debug_" + area + "_" + crop_img_counter + ".jpg");
            }

            api.saveMatImage(croppedImg, "paper_crop_" + area + "_" + crop_img_counter++ + ".jpg");

            return croppedImg;
        } else {
            int imgWidth = grayImg.width();
            int imgHeight = grayImg.height();

            int width = (int)(imgWidth * 0.8);
            int height = (int)(width * 15.0 / 27.0);

            int startX = (int)(imgWidth * 0.1);
            int startY = (imgHeight - height) / 2;

            Log.e("xString", "Unable to find tag of area '" + area + "' (ID: " + targetId + ")");

            Rect cropRect = new Rect(startX, startY, width, height);
            Mat croppedImg = new Mat(grayImg, cropRect);

            api.saveMatImage(croppedImg, "paper_crop_" + area + "_" + crop_img_counter++ + ".jpg");

            return croppedImg;
        }
    }
}
