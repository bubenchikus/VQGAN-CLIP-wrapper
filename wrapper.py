import os
import sys
from faker import Faker
import time
from datetime import date
import random
import argparse
import pandas
import cv2


def paths_to_vars():
	WORKING_FOLDER = os.getcwd() + '/'
	COLORS_NAMES = pandas.read_csv(WORKING_FOLDER + 'sources/colorhexa_com.csv').Name.tolist()
	COLORS_NAMES = [_ for _ in COLORS_NAMES if len(_.split()) == 1]
	QUALITIES_NAMES = ['detailed', 'dynamic', 'blurry', 'noisy', 'random', 'textured', 'soft', 'cinematic', 'photography', 'polaroid',
	'photorealistic', 'hyperrrealistic', 'impressionism', 'rendered in unity', 'rays', 'fog', 'clouds', 'sparkles', 'light bulbs']
	return WORKING_FOLDER, COLORS_NAMES, QUALITIES_NAMES


def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('--example', help="print full example request (other request arguments will be ignored)", type=bool, default=False)
	parser.add_argument('--runtest', help="run test request (other request arguments (except --example) will be ignored)")
	parser.add_argument('--text', '-t', help="request text", type=str, default=None)
	parser.add_argument('--size', '-s', help="picture resolution", type=int, nargs=2, default=[150, 150])
	parser.add_argument('--iter', '-i', help="number of iterations", type=int, default=None)
	parser.add_argument('--num', '-n', help="number of pictures to generate", type=int, default=10)
	parser.add_argument('--optimiser', '-opt', help="optimiser from list: [Adam,AdamW,Adagrad,Adamax,DiffGrad,RAdam,RMSprop]", type=str, default=None)
	parser.add_argument('--iter_randomness', help="max deviation for number of iterations in percents", type=int, default=0)
	parser.add_argument('--word_randomness', help="max weight deviation for each request word in percents", type=int, default=0)
	parser.add_argument('--add_colors', help="add a little bit of color randomness", type=bool, default=False)
	parser.add_argument('--add_colors_2', help="add colors with 60/30/10 proportion", type=bool, default=False)
	parser.add_argument('--add_qualities', help="add random abstract qualities for more interesting result", type=bool, default=False)
	parser.add_argument('--beep', help="beep when work is done", type=bool, default=False)
	parser.add_argument('--reduce_pink', help="VQGAN+CLIP tends to make pinkish pictures if too abstract request is given. Fix that!", type=bool, default=False)
	parser.add_argument('--initial_image', '-ii', help="initial image.", type=str, default=None)
	parser.add_argument('--generate_portrait', '-gp', help="generate portrait.", type=bool, default=False)
	parser.add_argument('--generate_character', '-gc', help="generate character.", type=bool, default=False)
	parser.add_argument('--save_every', '-se', help="save image iterations.", type=int, default=None)
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
	if args['add_colors_2']:
		proportions = [60, 30, 10]
		for i in range(3):
			words_from_request.append(f"{random.choice(args['COLORS_NAMES'])} color:{proportions[i]}")
	if args['add_qualities']:
		for sample in random.sample(args['QUALITIES_NAMES'], random.randint(2,5)):
			words_from_request.append(f"{sample}:{random.randint(10,80)}")
	if args['reduce_pink']:
		for bad_color in ['pink:-40', 'purple:-30', 'velvet:-30', 'magenta:-40', 'cyan:-10']:
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


def general_generator(args, n, fake):
	optimiser = choose_optimiser(args)
	it = randomize_iter(args)
	text = randomize_text(args)
	print(f"\n\nImage #{n+1}/{args['num']}:\nITERS: {it}\nSIZE: {args['size']}")
	picture_name = f"{date.today()}/{fake.pystr(max_chars=8)}-{optimiser}-{it}it-{args['size'][0]}x{args['size'][1]}.png"
	request = f"python {args['WORKING_FOLDER']}VQGAN-CLIP/generate.py -p '{text}' -s {args['size'][0]} {args['size'][1]} -i {it} -opt {optimiser} --output {picture_name} -se {args['save_every']}"
	if args['initial_image']:
		request += f" -ii {args['initial_image']}"
	os.system(request)
	while not os.path.exists(f"{args['WORKING_FOLDER']}/{picture_name}"):
		time.sleep(1)	


def generate_images(args, fake):
	if args['iter'] is None:
		args['iter'] = 50
	for n in range(args['num']):
		general_generator(args, n, fake)


def generate_portrait(args, fake):
	pictures_folder = args['WORKING_FOLDER'] + 'sources/base_face/'
	pictures = [pictures_folder + _ for _ in os.listdir(pictures_folder)]

	for n in range(args['num']):
		if args['iter'] is None:
			if args['optimiser'] == 'RMSprop':
				args['iter'] = 50
			else:
				args['iter'] = 100
		args['text'] = f"portrait painting:100|{random.choice(args['COLORS_NAMES'])} hair:50|{random.choice(['pale', 'beige', 'brown', 'black'])} skin:50|{random.choice(args['COLORS_NAMES'])} background:50"
		args['initial_image'] = random.choice(pictures)
		img = cv2.imread(args['initial_image'])
		args['size'] = [img.shape[1], img.shape[0]]
		general_generator(args, n, fake)


def generate_character(args, fake):
	pictures_folder = args['WORKING_FOLDER'] + 'sources/base_body/'
	pictures = [pictures_folder + _ for _ in os.listdir(pictures_folder)]
	args['text'] = f"human figure:100|detailed outfit:70"
	if args['iter'] is None:
		args['iter'] = 100
	for n in range(args['num']):
		args['initial_image'] = random.choice(pictures)
		img = cv2.imread(args['initial_image'])
		args['size'] = [img.shape[1], img.shape[0]]
		generate_image(args, n, fake)
		

def beep():
	os.system('play -nq -t alsa synth {} sine {}'.format(2, 240))


if __name__ == '__main__':
	args = parse()

	fake = Faker()
	Faker.seed(time.time())
	args['WORKING_FOLDER'], args['COLORS_NAMES'], args['QUALITIES_NAMES'] = paths_to_vars()
	create_session_folder(args['WORKING_FOLDER'])

	if (args['generate_portrait']):
		generate_portrait(args, fake)
	elif (args['generate_character']):
		generate_character(args, fake)
	elif type(args['text']) == str:
		args['text'] += ':100'
		generate_images(args, fake)
	else:
		print("WRAPPER: this program can't work without text input")
	
	if args['beep']:
		beep()
