import os
import json
import re
import tarfile
import uuid
from pathlib import Path
import xml.etree.ElementTree as ET

def validate_xml_file(file_path):
    """
    Validates an XML file for well-formedness.

    Args:
        file_path (str): Path to the XML file to validate.

    Returns:
        bool: True if the XML is well-formed, False otherwise.
    """
    try:
        # Parse the XML file
        ET.parse(file_path)
        print(f"XML file {file_path} is well-formed.")
        return True
    except ET.ParseError as e:
        # Print the error if the XML is not well-formed
        print(f"XML file {file_path} is not well-formed: {e}")
        return False


def validate_all_xml_files(directory):
    """
    Validates all XML files in the given directory and its subdirectories.

    Args:
        directory (str): The directory to search for XML files.

    Returns:
        None
    """
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(subdir, file)
                validate_xml_file(file_path)

# Define a function to sanitize content for XML
def sanitize_for_xml(content):
    return (content.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))

def remove_non_ascii(text):
    return ''.join(char for char in text if ord(char) < 128)

# Define a function to create directories for the course structure
def create_directories(base_path, directories):
    for directory in directories:
        dir_path = os.path.join(base_path, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def extract_video_urls(video_data_str):
    """Extract video URLs from the provided video data string."""
    urls = re.findall(r'https?://\S+', video_data_str)
    cleaned_urls = [url.rstrip(",") for url in urls]
    return cleaned_urls


def create_video_xml(vertical_id, video_data):
    """Generate XML with custom video player for a video content block based on provided video data."""

    # Extract video URLs
    video_urls = extract_video_urls(video_data)

    # Escape ampersands in video URLs
    video_urls = [sanitize_for_xml(url) for url in video_urls]

    const = "".replace(
        "&", "&amp;")

    # Check the number of video URLs to determine which template to use
    if len(video_urls) == 2:
        "https://player.vimeo.com/external/782853775"
        # Custom video player HTML for two video streams
        video_player_html = f"""
        <!-- Add the FontAwesome library -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css" />


<div id="main-container">
    <div id="video-container">
        <div class="video" id="video1Container">
            <video id="video1" preload="metadata" src="{video_urls[0]}{const}" style="background-color: var(--bg-color);"></video>
        </div>
        <div id="resizer"></div>
        <div class="video" id="video2Container">
            <video id="video2" preload="metadata" src="{video_urls[1]}{const}" style="background-color: var(--bg-color);"></video>
        </div>
    </div>
    <div id="controls">
		<i class="fas fa-play" onclick="togglePlay()"></i>
		<input type="range" min="0" max="100" value="0" id="progressBar" step="0.1" oninput="setProgress(this.value)" />
		<i class="fas fa-volume-up" onclick="toggleMute()"></i>
		<input type="range" min="0" max="1" step="0.01" value="1" id="volumeSlider" oninput="setVolume(this.value)" />
		<i class="fas fa-expand" onclick="toggleFullscreen()"></i>
		<i class="fas fa-moon" onclick="toggleDayNightMode()"></i>
	</div>

</div>

<style>
    :root {{
        --bg-color: white;
    }}

    body.dark-mode {{
        --bg-color: #333;
    }}

    #main-container {{
        position: relative;
    }}

    #video-container {{
        display: flex;
        width: 100%;
        height: 60vh;
        background-color: var(--bg-color);
    }}

    .video {{
        overflow: hidden;
        min-width: 10%;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: var(--bg-color);
    }}

    #resizer {{
		cursor: ew-resize;
		background-color: #888;  /* This color will make the resizer more visible */
		width: 10px;
		height: 100%;
		z-index: 1000;
	}}

    video {{
        object-fit: contain;
        max-height: 100%;
		max-width: 100%;
		background-color: var(--bg-color);
	}}
	
	.video video {{
		margin: auto;
	}}
	
	.fullscreen video {{
		width: 100%;
		height: 100%;
	}}

	.fullscreen #resizer {{
		height: 15px;
	}}
	
	#video1Container, #video2Container {{
		width: 50%;
	}}
	
	.icon-active {{
		color: green;
	}}

	#controls {{
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px;
	}}

	#progressBar {{
		flex: 1;
		margin: 0 10px;
		max-width: 50%;
	}}
</style>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
<![CDATA[	
	var video1, video2, container, ratio1, ratio2;
	
	function togglePlay() {{
		if (video1.paused) {{
			video1.play();
			video2.play();
			$('.fa-play').addClass('icon-active');
		}} else {{
			video1.pause();
			video2.pause();
			$('.fa-play').removeClass('icon-active');
		}}
	}}

	function setProgress(value) {{
		video1.currentTime = video1.duration * (value / 100);
		video2.currentTime = video2.duration * (value / 100);
	}}
	
	function toggleMute() {{
		if (video1.muted) {{
			video1.muted = false;
			video2.muted = false;
			$('.fa-volume-up').removeClass('icon-active');
		}} else {{
			video1.muted = true;
			video2.muted = true;
			$('.fa-volume-up').addClass('icon-active');
		}}
	}}

	function setVolume(value) {{
		video1.volume = value;
		video2.volume = value;
	}}

	var userHasResized = false;

	function toggleFullscreen() {{
		if (!document.fullscreenElement) {{
			if (container.requestFullscreen) {{
				container.requestFullscreen();
			}} else if (container.webkitRequestFullscreen) {{
				container.webkitRequestFullscreen();
			}} else if (container.mozRequestFullScreen) {{
				container.mozRequestFullScreen();
			}} else if (container.msRequestFullscreen) {{
				container.msRequestFullscreen();
			}}
		}} else {{
			if (document.exitFullscreen) {{
				document.exitFullscreen();
			}} else if (document.webkitExitFullscreen) {{
				document.webkitExitFullscreen();
			}} else if (document.mozCancelFullScreen) {{
				document.mozCancelFullScreen();
			}} else if (document.msExitFullscreen) {{
				document.msExitFullscreen();
			}}
		}}
	}}

	function toggleDayNightMode() {{
		document.body.classList.toggle('dark-mode');
	}}

	// Function to update the video ratios
	function updateRatios() {{
		var containerWidth = $('#video-container').width();
		ratio1 = $('#video1Container').width() / $('#video-container').width() * 100;
		ratio2 = $('#video2Container').width() / $('#video-container').width() * 100;
	
	}}
	
	function adjustVideoContainerWidths() {{
		var resizerWidthPercentage = $('#resizer').width() / $('#video-container').width() * 100;
		$('#video1Container').css('width', `calc(${{ratio1}}% - ${{resizerWidthPercentage / 2}}%)`);
		$('#video2Container').css('width', `calc(${{ratio2}}% - ${{resizerWidthPercentage / 2}}%)`);
	}}
	
	function firstFullscreenAdjustment() {{
		if (document.fullscreenElement) {{
			adjustVideoContainerWidths();
			document.removeEventListener('fullscreenchange', firstFullscreenAdjustment);
		}}
	}}
	
    $(document).ready(function() {{
        video1 = document.getElementById('video1');
        video2 = document.getElementById('video2');
        container = document.getElementById('video-container');

        video1.addEventListener('click', togglePlay);
        video2.addEventListener('click', togglePlay);

        video1.addEventListener('play', function() {{
            video2.play();
        }});

        video1.addEventListener('pause', function() {{
            video2.pause();
        }});

        video1.addEventListener('timeupdate', function() {{
            if (Math.abs(video1.currentTime - video2.currentTime) > 0.5) {{
                video2.currentTime = video1.currentTime;
            }}
            document.getElementById("progressBar").value = (video1.currentTime / video1.duration) * 100;
        }});

        video1.addEventListener('seeked', function() {{
            video2.currentTime = video1.currentTime;
        }});
		
		document.addEventListener('fullscreenchange', firstFullscreenAdjustment);
		
        var isResizing = false;
        var minWidth = 100; // minimum width of a video in pixels

        // Initializing the ratios right after their declaration
        ratio1 = $('#video1Container').width() / $('#video-container').width();
        ratio2 = $('#video2Container').width() / $('#video-container').width();

		$('#resizer').on('mousedown', function(event) {{
			isResizing = true;
			userHasResized = true;
			var initialX = event.clientX;
			var initialWidth1 = $('#video1Container').width();
			var initialWidth2 = $('#video2Container').width();
			var containerWidth = $('#video-container').width();

			$(document).on('mousemove', function(event) {{
				if (isResizing) {{
					var deltaX = event.clientX - initialX;
					var newWidth1 = initialWidth1 + deltaX;
					var newWidth2 = initialWidth2 - deltaX;

					// Updated conditions to ensure videos don't resize beyond set minimum width
					if (newWidth1 > minWidth && newWidth2 > minWidth) {{
						$('#video1Container').css('width', newWidth1 + 'px');
						$('#video2Container').css('width', newWidth2 + 'px');
						updateRatios();
					}}
				}}
			}});

			$(document).on('mouseup', function() {{
				isResizing = false;
				$(document).off('mousemove');
			}});
		}});

		document.addEventListener('fullscreenchange', function() {{
			// Use requestAnimationFrame to delay the execution until after the browser paints the new layout
			requestAnimationFrame(function() {{
				if (document.fullscreenElement) {{
					// Adjust videos to fill their containers in fullscreen
					$('video').css({{'width': '100%', 'height': '100%'}});
					adjustVideoContainerWidths();  // Adjust the container widths now
				}} else {{
					// Reset dimensions of the video elements when exiting fullscreen
					$('video').css({{'width': '', 'height': ''}});
					adjustVideoContainerWidths();
				}}
			}});
		}});

		updateRatios();
	}});
]]>
</script>
        """
        video_xml_structure = f"<video url_name='{vertical_id}'>{video_player_html}</video>" \

    elif len(video_urls) == 1:
        # Default player for one video stream
        video_template = """
        <div class="video" id="{video_id}Container">
            <iframe src="{video_url}" width="100%" height="100%" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen="true"></iframe>
        </div>
        """
        video_elements = video_template.format(video_id=f"video{uuid.uuid4().hex[:8]}", video_url=f"{video_urls[0]}{const}".replace("&", "&amp;"))
        video_xml_structure = f"""
        <video url_name="video_{vertical_id}">
            {video_elements}
        </video>
        """
    else:
        raise ValueError("Unexpected number of video URLs.")

    return video_xml_structure


def parse_questions_from_data(data):
    """Parse questions and their options from the provided data string."""
    # Extract blocks of questions and their options
    questions_blocks = re.findall(r"Question \d+.*?(?=Question \d+|$)", data, re.DOTALL)

    parsed_questions = []
    for block in questions_blocks:
        lines = block.strip().split("\n")

        # Check if the block has the expected multiple choice format
        if len(lines) >= 4 and "Pts" in lines[1]:
            question_text = lines[2]
            options = lines[3:]
        else:
            # Treat as an open-ended question
            question_text = lines[1]
            options = []

        parsed_questions.append({"text": question_text, "options": options})

    return parsed_questions


def create_problem_xml(vertical_id, questions):
    """Generate XML for a problem content block based on provided questions."""
    # Start with an opening vertical tag
    problems_xml = f'<vertical url_name="{vertical_id}">\n'

    for question in questions:
        # Ensure each question has a unique URL name
        question_id = uuid.uuid4().hex  # Generate a unique ID for each problem

        if "options" in question and question["options"]:
            # Multiple choice question
            choices_xml = "\n".join(
                [f'      <choice correct="false">{choice}</choice>' for choice in question["options"]])
            problem_structure = f"""
    <problem url_name="problem_{question_id}">
      <label>{sanitize_for_xml(question['text'])}</label>
      <multiplechoiceresponse>
        <choicegroup type="MultipleChoice">
{choices_xml}
        </choicegroup>
      </multiplechoiceresponse>
    </problem>\n"""
            problems_xml += problem_structure
        else:
            # Open-ended question
            problem_structure = f"""
    <problem url_name="problem_{question_id}">
      <label>{sanitize_for_xml(question['text'])}</label>
      <stringresponse answer=".*" type="text">
        <textline size="40"/>
      </stringresponse>
    </problem>\n"""
            problems_xml += problem_structure

    # Close the vertical tag
    problems_xml += '</vertical>'

    return problems_xml

def create_video_verticals(vertical_id, video_data):
    # Extract video URLs
    video_urls = extract_video_urls(video_data)

    # Escape ampersands in video URLs
    video_urls = [sanitize_for_xml(url) for url in video_urls]

    # Create custom HTML video player vertical
    custom_player_html = create_video_xml("custom_html_" +vertical_id , video_data)
    custom_player_vertical = f"<vertical url_name='custom_html_{vertical_id}'>{custom_player_html}</vertical>"

    # Create standard video component vertical
    # Default player for one video stream
    video_template = """
    <vertical url_name="video_{vertical_id}">
    <video url_name='video_{vertical_id}' display_name="Video" edx_video_id="" html5_sources='["https://player.vimeo.com/external/782568001.m3u8?s=bbf8f7be44c58895b7fb020dee561ad80569e9d0&logging=false"]' youtube_id_1_0="">
        <source src="{video_url}"/>
    </video>
    </vertical>"""
    standard_video_component = video_template.format(vertical_id=vertical_id,
                                           video_url=f"{video_urls[0]}").replace("&", "&amp;")
    # Return both vertical XMLs
    return custom_player_vertical, standard_video_component


# Define functions to generate XML for each type of content
def generate_chapter_xml(name, sequentials):
    sequential_refs = "".join([f'<sequential url_name="{sequential}" />' for sequential in sequentials])
    return f'<chapter url_name="{name}" display_name="{sanitize_for_xml(name)}">\n{sequential_refs}\n</chapter>\n'

def generate_sequential_xml(name, verticals):
    vertical_refs = "".join([f'<vertical url_name="{vertical}" />' for vertical in verticals])
    return f'<sequential url_name="{name}" display_name="{sanitize_for_xml(name)}">\n{vertical_refs}\n</sequential>\n'

def generate_vertical_xml(name, components):
    component_refs = "".join([f'<{component["type"]} url_name="{component["url_name"]}" />' for component in components])
    return f'<vertical url_name="{name}">\n{component_refs}\n</vertical>\n'

def generate_component_xml(name, type, content):
    if type == "html":
        return f'<html url_name="{name}">{sanitize_for_xml(content)}</html>\n'
    elif type == "problem":
        questions = parse_questions_from_data(content)
        return create_problem_xml(name, questions)
    elif type == "video":
        return create_video_xml(name, content)
    else:
        raise ValueError(f"Unsupported content type: {type}")

# Define function to write XML file
def write_xml_file(path, content):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

# Function to generate the course.xml file
def generate_course_xml(course_dir, org, course, url_name):
    course_xml_content = f'<course url_name="{url_name}" org="{org}" course="{course}"/>\n'

    course_xml_path = os.path.join(course_dir, 'course.xml')
    write_xml_file(course_xml_path, course_xml_content)
    return course_xml_path

def generate_course_index_xml(course_dir, chapters, url):
    course_xml_content = f'<course>\n'
    for chapter in chapters:
        course_xml_content += f'  <chapter url_name="{chapter}" />\n'
    course_xml_content += '</course>\n'

    course_xml_path = os.path.join(course_dir, f'{url}.xml')
    write_xml_file(course_xml_path, course_xml_content)


# Function to append new sequentials to an existing chapter XML
def append_to_chapter_xml(base_path, chapter_id, new_sequentials):
    chapter_path = os.path.join(base_path, 'chapter', f'{chapter_id}.xml')
    tree = ET.parse(chapter_path)
    chapter = tree.getroot()
    for sequential_id in new_sequentials:
        sequential_element = ET.SubElement(chapter, 'sequential')
        sequential_element.set('url_name', sequential_id)
    tree.write(chapter_path)


# Function to generate the entire course structure from the JSON data
def generate_full_course_structure(json_data, base_path):
    chapters = []
    sequentials = []
    verticals = []

    for section_id, section_data in json_data.items():
        chapter_id = f"chapter_{section_id}"
        chapters.append(chapter_id)

        # Generate chapter XML
        chapter_xml = generate_chapter_xml(chapter_id, [])
        write_xml_file(os.path.join(base_path, 'chapter', f'{chapter_id}.xml'), chapter_xml)

        # Depending on the content type, generate the appropriate XML
        content_type = section_data.get("type", "").lower()
        content_data = section_data.get("data", "")

        if content_type == "video":
            vertical_id = f"vertical_{section_id}"
            verticals.append(vertical_id)

            # Create two sequences: one for standard video and one for custom HTML
            standard_video_sequential_id = f"video_sequential_{section_id}"
            custom_html_sequential_id = f"custom_html_sequential_{section_id}"
            sequentials.extend([standard_video_sequential_id, custom_html_sequential_id])

            # Generate verticals for standard video and custom player
            custom_player_vertical_xml, standard_video_vertical_xml = create_video_verticals(vertical_id, content_data)
            write_xml_file(os.path.join(base_path, 'html', f'custom_html_{vertical_id}.xml'),
                           custom_player_vertical_xml)
            write_xml_file(os.path.join(base_path, 'video', f'video_{vertical_id}.xml'), standard_video_vertical_xml)

            # Generate sequential XML for standard video
            standard_video_sequential_xml = generate_sequential_xml(standard_video_sequential_id,
                                                                    [f"video_{vertical_id}"])
            write_xml_file(os.path.join(base_path, 'sequential', f'{standard_video_sequential_id}.xml'),
                           standard_video_sequential_xml)

            # Generate sequential XML for custom HTML player
            custom_html_sequential_xml = generate_sequential_xml(custom_html_sequential_id,
                                                                 [f"custom_html_{vertical_id}"])
            write_xml_file(os.path.join(base_path, 'sequential', f'{custom_html_sequential_id}.xml'),
                           custom_html_sequential_xml)

            # Append these sequentials to the chapter
            append_to_chapter_xml(base_path, chapter_id, [standard_video_sequential_id, custom_html_sequential_id])

        else:
            # For other content types, create a single sequential and vertical
            sequential_id = f"sequential_{section_id}"
            sequentials.append(sequential_id)

            vertical_id = f"vertical_{section_id}"
            verticals.append(vertical_id)

            # Generate sequential XML
            sequential_xml = generate_sequential_xml(sequential_id, [vertical_id])
            write_xml_file(os.path.join(base_path, 'sequential', f'{sequential_id}.xml'), sequential_xml)

            # Depending on the content type, generate the appropriate XML
            content_type = section_data.get("type", "").lower()
            content_data = section_data.get("data", "")
            if content_type == "text":
                content_xml = generate_component_xml(f"text_{vertical_id}", "html", content_data)
                write_xml_file(os.path.join(base_path, 'html', f'text_{vertical_id}.xml'), content_xml)
                content_ref = {"type": "html", "url_name": f"text_{vertical_id}"}
            elif content_type == "self-test" or content_type == "survey":
                content_xml = generate_component_xml(f"problem_{vertical_id}", "problem", content_data)
                write_xml_file(os.path.join(base_path, 'problem', f'problem_{vertical_id}.xml'), content_xml)
                content_ref = {"type": "problem", "url_name": f"problem_{vertical_id}"}
            else:
                # Handle other types or default to a placeholder for unknown types
                content_ref = {"type": "html", "url_name": f"text_{vertical_id}"}
                content_xml = f'<html url_name="text_{vertical_id}">Unsupported content type: {content_type}</html>\n'
                write_xml_file(os.path.join(base_path, 'html', f'text_{vertical_id}.xml'), content_xml)

            # Generate vertical XML
            vertical_xml = generate_vertical_xml(vertical_id, [content_ref])
            write_xml_file(os.path.join(base_path, 'vertical', f'{vertical_id}.xml'), vertical_xml)

            # Append the sequential to the chapter
            append_to_chapter_xml(base_path, chapter_id, [sequential_id])

    org = "HPI"
    course = "qc-optimization2023"
    url_name = "2023"

    # Generate the course.xml file
    course_xml_path = generate_course_xml(base_path, org, course, url_name)
    generate_course_index_xml(base_path + "/course", chapters, url_name)

    return course_xml_path, chapters, sequentials, verticals

# Now we'll create the .tar.gz package
def create_tar_gz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

# Define the base course directory and the required subdirectories
base_course_dir = 'test/output/openedx_course_structure'
subdirectories = ['chapter', 'course', 'sequential', 'vertical', 'html', 'problem', 'video', 'about', 'policies', 'assets', 'info']

# Create the base directory and subdirectories
create_directories(base_course_dir, subdirectories)

# Load the course data from the JSON file
json_file_path = 'test/input/qc-optimization2023.json'
with open(json_file_path, 'r') as json_file:
    course_data = json.load(json_file)

# Generate the full course structure
course_xml_path, chapters, sequentials, verticals = generate_full_course_structure(course_data, base_course_dir)

validate_all_xml_files(f'test/output/{Path(base_course_dir).name}/')

# Define the output path for the tar.gz file
output_tar_gz_path = f'test/output/{Path(base_course_dir).name}.tar.gz'
create_tar_gz(output_tar_gz_path, base_course_dir)

# Print the path to the tar.gz file for download
print(f"Packaged course is available at: {output_tar_gz_path}")

