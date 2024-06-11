from wand.image import Image
import sys

kmeans_values = [8, 16, 24, 32, 64]

def process (img):

    img.resize(1920, 1080)

    img.brightness_contrast(1, 5)
    img.white_balance()

    mask = img.clone()
    mask.type = 'grayscale'

    mask.threshold(0.7)
    mask.negate()
    mask.blur(3, 5)

    mask.alpha_channel = True

    opacity = 0.25
    mask.evaluate(operator='set', value=mask.quantum_range*opacity, channel='alpha')

    img.composite_channel('composite_channels', mask, 'darken')

    outputs = []
    for k in kmeans_values:
        _k = img.clone()

        _k.kmeans(number_colors=k, max_iterations=100, tolerance=0.01)

        outputs.append(_k)

    return outputs

def export(outputs, outPath):

    outPath_split = outPath.split('.')

    for o, k in zip(outputs, kmeans_values):

        o.save(filename = outPath_split[0]+'-K'+str(k)+'.'+outPath_split[1])
    

if __name__ == "__main__":

    args = sys.argv

    if len(args) < 2:
        exit()

    inPath = args[1]
    outPath = args[2]

    with Image(filename=inPath) as img:

        print ("PROCESSING " + inPath)

        outputs = process(img)

        export(outputs, outPath)
