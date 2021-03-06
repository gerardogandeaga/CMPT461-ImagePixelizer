
# In order to work from any directory, you can use this simple deploy script that deploys the 
# extension code along with its dependencies to the krita resources library. 
# THIS SCRIPT MUST BE CALLED FOR EVERY CHANGE TO THE PYTHON CODE!

OS=$1

# Krita location resources directory on mac
KRITA_RESOURCES_DIR="$HOME/Library/Application Support/krita/pykrita"
if [ "$OS" == "mac" ]; then
	KRITA_RESOURCES_DIR="$HOME/Library/Application Support/krita/pykrita"
fi
if [ "$OS" == "windows" ]; then
	KRITA_RESOURCES_DIR="%APPDATA%\krita\pykrita"
fi
if [ "$OS" == "linux" ]; then
	KRITA_RESOURCES_DIR="$HOME/.local/share/krita/pykrita"
fi

mkdir -p "$KRITA_RESOURCES_DIR" # create the pykrita directory if needed

EXTENSION_NAME="dynapix"
EXTENSION_DIR="$KRITA_RESOURCES_DIR/$EXTENSION_NAME"
LIB_DIR="$KRITA_RESOURCES_DIR/deps"
# TODO: Add to the list of dependencies if needed
PROJECT_DEPENDECIES="requirements.txt"
# create a python3.9 virtual environment and update
# NOTE: the python version has to match the version of python krita is running on!, 
# this may change. For now its 3.9.1 
PYTHON=python3.9

# clean the folder from our items
rm -rf "$EXTENSION_DIR" "$KRITA_RESOURCES_DIR/$EXTENSION_NAME.desktop"

# the virtual environment doesnt exist then create it
if [ ! -d "$LIB_DIR" ] 
then
	echo "Creating " $PYTHON " virtual environment..."
	$PYTHON -m venv "$LIB_DIR"
fi

echo "Installing Project Dependecies..."
source "$LIB_DIR/bin/activate"
python -m pip install --upgrade pip
pip install wheel

# install project dependencies
pip install -r "$(pwd)/$PROJECT_DEPENDECIES"

# exit
deactivate

if [ ! -d "$EXTENSION_NAME/core/xt_consistency/models" ]
then
	echo "Downloading XT-Consistency Pre-Trained normal model..."
	mkdir "./$EXTENSION_NAME/core/xt_consistency/models"
	wget -O "./$EXTENSION_NAME/core/xt_consistency/models/rgb2normal_consistency.pth" https://www.dropbox.com/s/6yu48alcava3pcx/rgb2normal_consistency.pth?dl=1
fi

# copy extension into the krita Resource directory
echo "Copying source code..."
cp -R "$EXTENSION_NAME/" "$EXTENSION_DIR"
cp "$EXTENSION_NAME.desktop" "$KRITA_RESOURCES_DIR"

# create a path output file for the plugin to read
echo "$LIB_DIR/lib/$PYTHON/site-packages" > "$EXTENSION_DIR/lib"

rm -rf "$EXTENSION_DIR/__pycache__/" "$EXTENSION_DIR/*.code-workspace"

echo "Done!"
