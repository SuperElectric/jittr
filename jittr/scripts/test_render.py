from panda3d.core import loadPrcFileData
from panda3d.core import WindowProperties
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Renders a .egg file to an image file in current folder")

    parser.add_argument('--width',
                        type=int,
                        default=300,
                        help="The width of the output image")

    parser.add_argument('--height',
                        type=int,
                        default=200,
                        help="The height of the output image")

    parser.add_argument('-i',
                        '--input',
                        default="../assets/panda-model.egg.pz",
                        help="The .egg file to render")

    result = parser.parse_args()

    return result

def render(obj_file_path, width, height):
    loadPrcFileData('', 'win-size ' + str(width) + ' ' + str(height) )
    from direct.showbase.ShowBase import ShowBase
    base = ShowBase()
    base.model = base.loader.loadModel(obj_file_path)
    base.model.setPos(0,4000,0);
    base.model.reparentTo(base.render)
    base.graphicsEngine.renderFrame()
    base.screenshot(namePrefix = 'render')
    base.run()

def main():

    args = parse_args()
    render(args.input, args.width, args.height)


# Runs this code if this file is executed as a script.
if __name__ == "__main__":
    main()
