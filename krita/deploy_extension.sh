# In order to work from any directory, you can use this simple deploy script that deploys the 
# extension code along with its dependencies to the krita resources library. 
# THIS SCRIPT MUST BE CALLED FOR EVERY CHANGE TO THE PYTHON CODE!

# Krita location resources directory on mac
KRITA_RESOURCES_DIR="$HOME/Library/Application Support/krita/pykrita"
mkdir -p "$KRITA_RESOURCES_DIR" # create the pykrita directory if needed

EXTENSION_NAME="my_extension"
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

echo "Copying source code..."

cp -R "$EXTENSION_NAME/" "$EXTENSION_DIR"
cp "$EXTENSION_NAME.desktop" "$KRITA_RESOURCES_DIR"

# create a path output file for the plugin to read
echo "$LIB_DIR/lib/$PYTHON/site-packages" > "$EXTENSION_DIR/lib"

rm -rf "$EXTENSION_DIR/__pycache__/" "$EXTENSION_DIR/*.code-workspace"

echo "Done!"
