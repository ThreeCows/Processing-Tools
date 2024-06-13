from wand.image import Image
import sys
import glob 

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

        o.save(filename = outPath_split[0]+'-K'+str(k)+'.'+outPath_split[-1])
    

if __name__ == "__main__":

    args = sys.argv

    if len(args) < 2:
        exit()

    inPath = args[1]
    outPath = args[2]

    numInitial = 0
    num = 0
    if len(args) > 3:
        numInitial = int(args[3])

    if outPath[-1] != '/':
        outPath = outPath + '/'

    length = len(glob.glob(inPath))
    outFolder = glob.glob(outPath + '*')
    outNames = []
    for o in outFolder:
        if "K8" in o:
            outNames.append(o.split('-K8')[0].split('/')[-1])

    for filepath in glob.iglob(inPath):

        num += 1

        if num < numInitial:
            continue
        
        name = filepath.split('/')[-1]

        if name.split('.')[0] in outNames:
            print ('Already processed: ' + name + "    " + str(num) + "/" + str(length))
            continue

        extension = str.lower(name.split('.')[-1])
        validExtensions = ['jpg', 'png', 'jpeg']

        if extension not in validExtensions:
            print ("Skipping: " + name + "    " + str(num) + "/" + str(length))
            continue

        print ("Processing: " + name + "    " + str(num) + "/" + str(length))
        
        

        with Image(filename=filepath) as img:

            outputs = process(img)

            export(outputs, outPath + name)