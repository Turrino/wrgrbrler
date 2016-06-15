from configparser import ConfigParser
import random
import json
from Manifest import Manifest, Peep, Place, Event
from PIL import Image, ImageFilter


class Wrgrbrler:
    def __init__(self, parsed_crumbs):
        self.crumbs = parsed_crumbs

    def any_of_many(self, crumblist, discard_item = True):
        randomness = random.randrange(0, len(crumblist))
        item = crumblist[randomness]
        if discard_item:
            crumblist.remove(item)
        return item

    def writerer(self, crumbset_key, subset=None):

        fetch_crumb = self.any_of_many

        def fetch_subset(words):
            pick = self.any_of_many(words)
            return pick[subset] if type(pick) is list else pick

        if subset is not None:
            fetch_crumb = fetch_subset

        wroted = ""

        crumbset = self.crumbs[crumbset_key]

        for list in crumbset:
            wroted = "{0} {1}".format(wroted, fetch_crumb(list))

        return wroted[1:]

    def get_peep(self, name, gender = None):
        if gender is None:
            gender = random.randrange(0, 2)
        return Peep(name, self.writerer('characters', gender), gender)

    def get_place(self, gender=None):
        return Place(self.writerer('locations'))

    def get_event(self, type):
        #to do
        return None


def drawerer():
    combined = Image.new('RGBA', (100, 300), color=50)

    part1 = Image.open('{0}.png'.format(random.randrange(1, 9)))
    part2 = Image.open('{0}.png'.format(random.randrange(1, 9)))
    part3 = Image.open('{0}.png'.format(random.randrange(1, 9)))

    combined.paste(part1, (0, 0))
    combined.paste(part2, (0, 100))
    combined.paste(part3, (0, 200))

    return combined

def main():

    parser = ConfigParser()
    parser.read('../config')

    crumbs = None
    with open('breadcrumbs') as crumbs_file:
        crumbs = json.load(crumbs_file)

    template_name = parser.get('setup', 'template')
    template = crumbs['templates'][template_name]
    # Assuming one event needs only place only - can change later
    events_count = len(template['events'])
    peep_count = int(parser.get('setup', 'peep_count'))
    peep_names = str.split(parser.get('setup', 'peep_names'), ',')

    if peep_count != len(peep_names):
        raise ValueError('Number of peeps ({0}) and number of peep names ({1}) provided does not match, fix the config.'
              .format(peep_count, len(peep_names)))

    garbler = Wrgrbrler(crumbs)

    drawed = drawerer()

    manifest = Manifest()

    peeps = manifest.peeps
    places = manifest.places
    events = manifest.events

    for x in range(0, peep_count):
        peeps.append(garbler.get_peep(peep_names[x]))

    for x in range(0, events_count):
        places.append(garbler.get_place())
        # get event of the type needed at this index by the template
        events.append(garbler.get_event(template['events'][x]['type']))




    # drawed.show()
    print('{0}, the {1}, went to a {2}, had lunch at a {3}, ended up in a {4}'
          .format(peeps[0].name, peeps[0].desc, places[0].name, places[1].name, places[2].name))
    print('{0} gender is {1}'.format(peeps[0].desc, peeps[0].gender, places[1].name, places[2].name))


if __name__ == '__main__':
    main()


