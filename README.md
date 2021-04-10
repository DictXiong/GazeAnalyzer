# GazeAnalyzer

We create this software to combine PsychoPy and BeGaze. Since SMI has been acquired by Apple in 2016, we find it hard to use the eye tracker of SMI directly inside PsychoPy. Therefore we use them separately (we get `csv` files from PsychoPy and `txt` files from i View X), and analyze them together with this software.

In `utils/idf_reader.py` we use [gazepath](https://CRAN.R-project.org/package=gazepath). It's an R package who can parse eye-tracking data into fixations. 
