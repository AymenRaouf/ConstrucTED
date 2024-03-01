# ConstrucTED : Constructing Tailored Educational Datasets From Online Courses
![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)


ConstrucTED is a tool built on top of Google APIs, enabling the efficient creation of custom educational datasets from YouTube playlists. It creates datasets from video course transcripts, providing a ready-to-use solution that significantly shortens the time required to create such datasets. The resulting datasets are versatile and suitable for tasks like classification
and learning path creation.


![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)


## Installation

Download the project then use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```bash
pip install -r requirements.txt
```
![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## Usage
- Before using ConstrucTED, you should first get a [Google API personal key](https://developers.google.com/youtube/v3/getting-started).
- Create a file called .env in the base of the project and add this line with your perosnal API key : 
```bash
GOOGLE_API_KEY='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```
- You can run the main.ipynb file to create datasets. 
- There are some pre-made input files in the <b>Input</b> folder. You can use these sample input files to create datasets. 
- The datasets that can be created using these sample input files are available in the <b>Output</b> folder for direct usage.
- You can create your own input files and use them in the code 
```python
input_file = 'path_to_your_input_file'
my_dataset.create_series(input_file)
my_dataset.save(path='path_to_an output_location')
```
- This code generates three files as explained in the article : series.csv, episodes.csv, and chapters.csv.
- These files contain the created dataset.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## License

[MIT](https://choosealicense.com/licenses/mit/)