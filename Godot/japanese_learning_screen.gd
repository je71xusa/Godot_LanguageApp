extends Node2D

@onready var japanese_label = $JapaneseWordLabel
@onready var romanji_label = $RomanjiLabel
@onready var audio_player = $AudioStreamPlayer2D
@onready var play_audio_button = $PlayAudioButton
@onready var choice_buttons = [$ChoiceButton1, $ChoiceButton2, $ChoiceButton3, $ChoiceButton4]

var all_rows = []
var current_index = 0
var db
var db_path = "res://JapaneseLearning"
var correct_answer_index = 0

func commitDatatoDB():
	db = SQLite.new()
	db.path = db_path
	db.open_db()

func load_and_shuffle_database():
	var query = "SELECT * FROM Words"
	db.query(query)
	all_rows = db.query_result
	all_rows.shuffle()

func generate_choices():
	if current_index >= all_rows.size():
		# Reset or end the game if you've gone through all rows
		return

	var correct_row = all_rows[current_index]
	var choices = [correct_row]

	while choices.size() < 4:
		var random_row = all_rows[randi() % all_rows.size()]
		if random_row != correct_row and random_row not in choices:
			choices.append(random_row)

	choices.shuffle()
	# After shuffling the choices, find the index of the correct answer
	correct_answer_index = choices.find(correct_row)

	# Update the UI with the choices
	japanese_label.text = correct_row["Japanese"]
	romanji_label.text = correct_row["Pronunciation"]
	audio_player.stream = load(correct_row["Audio"])  # Set the audio stream
	for i in range(4):
		choice_buttons[i].text = choices[i]["English"]

	current_index += 1

func _ready():
	commitDatatoDB()  # Open the database connection
	load_and_shuffle_database()
	generate_choices()
	audio_player.play()  # Play the audio automatically




# Function to handle choice button press
func handle_button_press(button_index):
	print("Button pressed with index:", button_index)
	var chosen_button = choice_buttons[button_index]
	
	# Determine the color (green for correct, red for incorrect)
	var final_color = Color(1, 0, 0, 1)  # Default to red
	if button_index == correct_answer_index:
		final_color = Color(0, 1, 0, 1)  # Green for the correct answer
	chosen_button.modulate = final_color
	
	if button_index != correct_answer_index:
		choice_buttons[correct_answer_index].modulate = Color(0, 1, 0, 1)  # Show the correct answer in green
	
	await get_tree().create_timer(3.0).timeout  # Wait for 3 seconds
	
	# Reset button color to white (or whatever the default is)
	for button in choice_buttons:
		button.modulate = Color(1, 1, 1, 1)  # RGBA for white
	generate_choices()


func _on_choice_button_1_pressed():
	handle_button_press(0)

func _on_choice_button_2_pressed():
	handle_button_press(1)

func _on_choice_button_3_pressed():
	handle_button_press(2)

func _on_choice_button_4_pressed():
	handle_button_press(3)
	
func _on_PlayAudioButton_pressed():
	print("Play audio button pressed")
	if audio_player.playing:
		audio_player.stop()  # Stop the audio if it's already playing
	else:
		audio_player.play()  # Play the audio
