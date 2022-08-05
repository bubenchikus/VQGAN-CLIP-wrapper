import os
import sys
from faker import Faker
from PIL import Image
import time
from datetime import date
import random
import argparse
import pandas


def paths_to_vars():
	WORKING_FOLDER = os.getcwd() + '/VQGAN-CLIP/'
	COLORS_NAMES = pandas.read_csv(os.getcwd() + 'sources/colorhexa_com.csv').Name.tolist()
	COLOR_NAMES = [_ for _ in COLORS_NAMES if len(_.split()) == 1]
	QUALITIES_NAMES = ['detailed', 'dynamic', 'blurry', 'noisy', 'random', 'textured', 'soft', 'cinematic', 'photography', 'polaroid',
	'photorealistic', 'hyperrrealistic', 'impressionism', 'rendered in unity', 'rays', 'fog', 'clouds', 'sparkles', 'light bulbs']
	return WORKING_FOLDER, COLORS_NAMES, QUALITIES_NAMES


def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('--example', help="print full example request (other request arguments will be ignored)", type=bool, default=False)
	parser.add_argument('--runtest', help="run test request (other request arguments (except --example) will be ignored)")
	parser.add_argument('--text', '-t', help="request text", type=str)
	parser.add_argument('--size', '-s', help="picture resolution", type=int, nargs=2, default=[150, 150])
	parser.add_argument('--iter', '-i', help="number of iterations", type=int, default=50)
	parser.add_argument('--num', '-n', help="number of pictures to generate", type=int, default=10)
	parser.add_argument('--optimiser', '-opt', help="optimiser from list: [Adam,AdamW,Adagrad,Adamax,DiffGrad,RAdam,RMSprop]", type=str, default=None)
	parser.add_argument('--iter_randomness', help="max deviation for number of iterations in percents", type=int, default=0)
	parser.add_argument('--word_randomness', help="max weight deviation for each request word in percents", type=int, default=0)
	parser.add_argument('--add_colors', help="add a little bit of color randomness", type=bool, default=False)
	parser.add_argument('--add_qualities', help="add random abstract qualities for more interesting result", type=bool, default=False)
	parser.add_argument('--beep', help="beep when work is done", type=bool, default=False)
	parser.add_argument('--reduce_pink', help="VQGAN+CLIP tends to make pinkish pictures if too abstract request is given. Fix that!", type=bool, default=False)
	args = vars(parser.parse_args())
	return args


def create_session_folder(WORKING_FOLDER):
	today = str(date.today()) + '/'
	if not os.path.exists(WORKING_FOLDER + today):
		os.makedirs(WORKING_FOLDER + today)


def randomize_iter(args):
	return random.randint(round(args['iter'] * (1 - args['iter_randomness'] / 100)), round(args['iter'] * (1 + args['iter_randomness'] / 100)))


def randomize_text(args):
	# words_from_request = [word + f":{random.randint(100 - args['word_randomness'], 100 + args['word_randomness'])}" for word in args['text'].split(' ')]
	words_from_request = [args['text']]
	if args['add_colors']:
		for sample in random.sample(args['COLORS_NAMES'], random.randint(1,3)):
			words_from_request.append(f"{sample} color:{random.randint(10,60)}")
	if args['add_qualities']:
		for sample in random.sample(args['QUALITIES_NAMES'], random.randint(2,5)):
			words_from_request.append(f"{sample}:{random.randint(10,80)}")
	if args['reduce_pink']:
		for bad_color in ['pink:-40', 'purple:-30', 'velvet:-30', 'magenta:-40', 'cyan:-10', 'blue:-10']:
			words_from_request.append(bad_color)
	final_text = '|'.join(words_from_request)
	return final_text


def choose_optimiser(args):
	optimisers = ['Adam', 'AdamW', 'Adagrad', 'Adamax', 'DiffGrad', 'RAdam', 'RMSprop']
	if args['optimiser'] is None or (args['optimiser'] not in optimisers):
		return random.choice(optimisers)
	return args['optimiser']


def generate_text():
	pass


def generate_images(args):
	fake = Faker()
	for n in range(args['num']):
		it = randomize_iter(args)
		text = randomize_text(args)
		optimiser = choose_optimiser(args)
		print(f"\n\nImage #{n+1}/{args['num']}:\nITERS: {it}\nSIZE: {args['size']}")
		Faker.seed(time.time())
		picture_name = f"{date.today()}/{fake.pystr(max_chars=8)}-{optimiser}-{it}it-{args['size'][0]}x{args['size'][1]}.png"
		os.system(f"python {args['WORKING_FOLDER']}generate.py -p '{text}' -s {args['size'][0]} {args['size'][1]} -i {it} -opt {optimiser} --output {picture_name}")
		while not os.path.exists(f"{args['WORKING_FOLDER']}/{picture_name}"):
			time.sleep(1)			


def beep():
	os.system('play -nq -t alsa synth {} sine {}'.format(2, 240))


if __name__ == '__main__':
	args = parse()
	args['WORKING_FOLDER'], args['COLORS_NAMES'], args['QUALITIES_NAMES'] = paths_to_vars()
	create_session_folder(args['WORKING_FOLDER'])
	generate_images(args)
	if type(args['text']) == str:
		generate_images(args)
	else:
		print("WRAPPER: this program can't work without text input")
	
	if args['beep']:
		beep()
