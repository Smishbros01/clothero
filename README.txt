**⚠️ NOTE: This is a legacy project. This was developed as an introductory Python college project. It is no longer actively maintained and serves as a record of my early development journey. For examples of my current technical standards, please see my [Blackjack Monte Carlo Simulator].

# Clothero: Virtual Closet Manager

Hello and welcome to Clothero! Here are some quick project details:

Intended Use:
- Clothero is intended to be used as a closet manager
- It can hold various wearable items such as shirts, pants, socks, shoes, jewelry, hats and more! 
- It acts as a virtual closet and from there you can generate daily outfits to wear based off of clothe color, material, professionalism or just complete randomness!

How to install dependencies:
- Download Anaconda
- Open your Terminal or Command Line and run
	- conda create -n venv anaconda

How to run Clothero:
- Open your Terminal or Command Line and run
	- conda activate venv
	- cd (find OutfitGen.py directory)
	- python OutfitGen.py
- Go to http://127.0.0.1:5000

How to use Clothero:
- All buttons are very self explanatory but here is a quick explanation for EVERYTHING Clothero can do for you
- Home (takes you to the front page which is what you started on)
- Generate Outfit (creates an outfit for you based off of selected criteria and pieces)
	- Random (completely random)
	- Color (only gives you outfits with your color selection(s))
	- Professionalism (gives you an outfit based off of how professional you want each piece to be)
	- Material (outfit based on the piece material chosen)
	- Favorites (outfit based only on favorited pieces)
- Closet (view/add/remove any piece you have sorted)
- Laundry (wash clothes so they can be put back into the generation pool)
- Search (find clothes that match criteria you have input)
- Settings
	- Edit Closet (edit section or piece info)
	- Laundry Settings (allows you to make items "unwashable" so that they always remain in the generation pool)
	- Unique Piece Settings (customize your home page unique piece generation)
	- Recently Trashed Items (re-add clothes you have recently deleted)
	- Reset (deletes all clothes and sections)


What outputs to expect:
- Outfit Generation
- Virtual Closet Visualization

Any setup instructions:
- Add any images you want to assign your clothes to into the /static/clothes folder
	- There is a preset closet so that you can see the functions of the website
	- In order to add your own clothes delete everything in the clothes folder EXCEPT unknown.jpg
		- Then go into the website and go to settings and click RESET
	- Now you can add your clothes into the clothes folder
	- When typing the image filename be sure to be EXACT


Limitations:
- Don't use - for any naming or descriptions on any clothing item
	- Will result in a Name Error, test it out!
- If an item is deleted, and its original section or piece name has been changed, re-adding it via the "Recently Trashed" setting will add it with the ORIGINAL section and piece names