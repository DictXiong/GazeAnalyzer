# GazeAnalyzer

We create this software to combine PsychoPy and BeGaze. Since SMI has been acquired by Apple in 2016, we find it hard to use the eye tracker of SMI directly inside PsychoPy. Hence we use them separately (we get `csv` file from PsychoPy and `txt` file from i View X), and analyze them together with this software.

Inside `utils/pygazeanalyser` is [PyGazeAnalyser](https://github.com/esdalmaijer/PyGazeAnalyser), an open-source toolbox for eye tracking. Some modifications were applied.