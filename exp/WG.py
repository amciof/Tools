import json
import math
import tkinter as tk

from random import uniform


#I/O operations
def read_graph_from_file(file_path):
	with open(file_path) as file:
		graph = json.load(file)

	return graph

def write_graph_to_disk(file_path, graph):
	with open(file_path, 'w') as file:
		json.dump(graph, file, indent=4)

	return None



#pack/unpack = represent graph in convinient format/back to unpacked form
def unpack_graph(packed_graph):
	points = {}
	for point in packed_graph['points']:
		point['pos'] = [0, 0]
		points[point['idx']] = point
		del(point['idx'])

	lines = {}
	for line in packed_graph['lines']:
		lines[line['idx']] = line
		del(line['idx'])

	packed_graph['points'] = points
	packed_graph['lines'] = lines


def pack_graph(unpacked_graph):
	packed_points = []
	for idx, point in unpacked_graph['points'].items():
		del(point['pos'])
		point['idx'] = idx

		packed_points.append(point)

	packed_lines = []
	for idx, line in unpacked_graph['lines'].items():
		line['idx'] = idx

		packed_lines.append(line)

	unpacked_graph['points'] = packed_points
	unpacked_graph['lines'] = packed_lines



#assignment to vertices plane positions
def assign_pos_centered(graph
	, radius_stride
	, center_x
	, center_y
):
	points = graph['points']

	count = len(points)
	if count == 0:
		return None

	sq_root = int(math.floor(math.sqrt(count)))
	radius = 0.0
	it = iter(points)

	for i in range(1, 2 * sq_root, 2):
		delta_angle = 2 * math.pi / i

		for j in range(i):
			point_key = next(it)

			points[point_key]['pos'] = \
				radius * math.cos(delta_angle * j) + center_x \
				, radius * math.sin(delta_angle * j) + center_y

		radius += radius_stride

	square = sq_root * sq_root
	if square != count:
		delta_angle = 2 * math.pi / (count - square)

		for j in range(count - square):
			point_key = next(it)

			points[point_key]['pos'] = \
				radius * math.cos(delta_angle * j) + center_x \
				, radius * math.sin(delta_angle * j) + center_y

	return None



#spring-force method
def create_adjacency_list(unpacked_graph):
    points = unpacked_graph['points']
    lines  = unpacked_graph['lines']

    adj_list = {idx : [] for idx in points}
    for line in lines:
        first, second = line['points'].values()
        length = line['length']

        adj_list[first].append({'point' : second, 'length' : length})
        adj_list[second].append({'point' : first , 'length' : length})

    return adj_list

def assign_bfs_based(adj_list):
	pass

def create_phys_sys(unpacked_graph, x_start, x_end, y_start, y_end, v_range):
    phys_sys = {}
    for idx in unpacked_graph['points']:
        phys_sys[idx] = {
            'r' : {'x' : uniform(x_start, x_end), 'y' : uniform(y_start, y_end)}
             , 'v' : {'x' : uniform(-v_range, v_range), 'y' : uniform(-v_range, v_range)}
             , 'f' : {'x' : 0.0, 'y' : 0.0}
        }
    return phys_sys

def assign_pos_spring(
	unpacked_graph       #
	, x_view , y_view    #
	, v_range            #
	, kc, q              # Coulomb
	, kh, scale, length  # Hooke
	, kf                 # Friction
	, dt                 #
	, eps                #
	, relaxations        # times to repeat
	, eps_energy
):
	phys_sys = create_phys_sys(unpacked_graph, 0, x_view, 0, y_view, v_range)
	all_idx  = list(phys_sys.keys())

	if len(all_idx) == 0:
		return None

	for r in range(relaxations):
		#reset
		for particle in phys_sys.values():
			particle['f'] = {'x' : 0.0, 'y' : 0.0}

		#Coulomb
		for i in range(len(all_idx)):
			particle_i = phys_sys[all_idx[i]]

			rx_i, ry_i = particle_i['r'].values()

			for j in range(i + 1, len(all_idx)):
				particle_j = phys_sys[all_idx[j]]

				rx_j, ry_j = particle_j['r'].values()

				f_x = rx_i - rx_j
				f_y = ry_i - ry_j

				norm = math.sqrt(f_x**2 + f_y**2)
				norm = norm if norm > eps else eps

				f_x /= norm
				f_y /= norm

				force = kc * q**2 / norm**2

				particle_i['f']['x'] += force * f_x
				particle_i['f']['y'] += force * f_y
				particle_j['f']['x'] -= force * f_x
				particle_j['f']['y'] -= force * f_y

		#Hooke
		for line in unpacked_graph['lines'].values():
			first, second = line['points']

			particle_1 = phys_sys[first]
			particle_2 = phys_sys[second]

			rx_1, ry_1 = particle_1['r'].values()
			rx_2, ry_2 = particle_2['r'].values()

			f_x = rx_1 - rx_2
			f_y = ry_1 - ry_2

			norm = math.sqrt(f_x**2 + f_y**2)
			norm = norm if norm > eps else eps

			f_x /= norm
			f_y /= norm

			dl = norm / scale - length

			particle_1['f']['x'] -= kh * dl * f_x
			particle_1['f']['y'] -= kh * dl * f_y
			particle_2['f']['x'] += kh * dl * f_x
			particle_2['f']['y'] += kh * dl * f_y

		#Friction
		for particle in phys_sys.values():
			vx, vy = particle['v'].values()

			particle['f']['x'] -= kf * vx 
			particle['f']['y'] -= kf * vy

		#update
		ke = 0.0
		for particle in phys_sys.values():
			particle['v']['x'] += particle['f']['x'] * dt
			particle['v']['y'] += particle['f']['y'] * dt

			particle['r']['x'] += particle['v']['x'] * dt
			particle['r']['y'] += particle['v']['y'] * dt

			ke += (particle['v']['x']**2 + particle['v']['y']**2) / 2

		if ke < eps_energy:
			break

		print('%i : %lf' % (r, ke))

	#viewport transform
	#bounds
	x_left , y_up   = phys_sys[all_idx[0]]['r'].values()
	x_right, y_down = x_left, y_up
	for elem in phys_sys.values():
		x, y = elem['r'].values()

		x_left  = x_left  if x_left  < x else x
		x_right = x_right if x_right > x else x

		y_up   = y_up   if y_up   > y else y
		y_down = y_down if y_down < y else y

	#center & embed
	dx = (x_right - x_left)
	dy = (y_up    - y_down)
	for elem in phys_sys.values():
		x, y = elem['r'].values()

		elem['r']['x'] = (x - x_left) / dx * x_view
		elem['r']['y'] = (y - y_down) / dy * y_view

	#assign
	points = unpacked_graph['points']
	for idx, elem in phys_sys.items():
		points[idx]['pos'] = list(elem['r'].values())
		
	return None


def draw_graph(graph
	, place
	, point_size
	, label_size
	, edge_color
	, label_color
	, point_color
):
	label_size //= 2
	point_size //= 2

	points = graph['points']
	lines = graph['lines']

	for idx, line in lines.items():
		p0, p1 = line['points']
		x0, y0 = points[p0]['pos']
		x1, y1 = points[p1]['pos']
		place.create_line(x0, y0, x1, y1, fill=edge_color)

		xc = x0 + (x1 - x0) // 2
		yc = y0 + (y1 - y0) // 2
		place.create_oval(
			xc - label_size, yc - label_size
			, xc + label_size, yc + label_size
			, fill=label_color
		)
		place.create_text(xc, yc, text=str(line['length']), justify=tk.CENTER, font="Verdana 8")

	for idx, point in points.items():
		x0, y0 = point['pos']
		place.create_oval(
			x0 - point_size, y0 - point_size
			, x0 + point_size, y0 + point_size
			, fill=point_color
			)
		place.create_text(x0, y0, text=str(idx), justify=tk.CENTER, font="Verdana 8")
		


def main(wt, ht):
	graph = read_graph_from_file('Data/small_graph.json')
	unpack_graph(graph)

	top = tk.Tk()
	canv = tk.Canvas(top, bg='light gray', height=ht, width=wt)

	assign_pos_spring(
		graph
		, wt, ht
		, 5000
		, kc = 1, q = 0.01
		, kh = 1500, scale = 10, length = 1
		, kf = 30
		, dt = 0.01
		, eps = 1e-6
		, relaxations = 20
		, eps_energy = 1e-9
	)
	draw_graph(graph, canv, 18, 12, 'black', 'yellow', 'red')
	
	pack_graph(graph)
	write_graph_to_disk('Data/my_graph.json', graph)
	
	canv.pack()
	top.mainloop()



if __name__ == '__main__':
	main(1500, 900)