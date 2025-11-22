import re
import sys

# The CSS and JS required for the interactive quiz
CSS_BLOCK = """
<style>
  /* Quiz Styles */
  .quiz-block {
    margin-bottom: 40px;
    padding: 20px;
  }
  
  .quiz-options {
    list-style: none;
    padding: 0;
    margin-top: 15px;
  }

  .option {
    padding: 10px 15px;
    margin-bottom: 8px;
    cursor: pointer;
    border: 1px solid gray;
    transition: all 0.2s ease;
  }

  .option:hover {
    border: 1px solid white;
  }

  .quiz-block.answered .option {
    cursor: default;
    pointer-events: none;
  }

  .quiz-block.answered .option.correct {
    color: #155724;
    font-weight: bold;
  }

  .quiz-block.answered .option:not(.correct) {
    color: #86181d;
    opacity: 0.7;
  }

  .explanation {
    display: none;
    margin-top: 15px;
    padding: 15px;
  }

  .quiz-block.answered .explanation {
    display: block;
    animation: fadeIn 0.5s;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
</style>
"""

JS_BLOCK = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  var options = document.querySelectorAll('.option');
  options.forEach(function(option) {
    option.addEventListener('click', function() {
      var block = this.closest('.quiz-block');
      if (block.classList.contains('answered')) return;
      block.classList.add('answered');
    });
  });
});
</script>
"""

def convert_jekyll_quiz(md_content):
    """
    Parses the custom Jekyll quiz format and returns the interactive HTML version.
    """
    
    # 1. Extract and preserve Front Matter
    front_matter_match = re.match(r'^---(.*?)---', md_content, re.DOTALL)
    if front_matter_match:
        front_matter = front_matter_match.group(0)
        # Remove front matter from content to parse
        content = md_content[len(front_matter):]
    else:
        front_matter = ""
        content = md_content

    # 2. Convert custom code blocks (-c ... -) to standard markdown fenced blocks
    # Regex looks for -c at start of line, captures content, ends with - at start of line
    content = re.sub(r'(?m)^-c\s*\n(.*?)\n-$', r'```c\n\1\n```', content, flags=re.DOTALL)

    # 3. Split content by "### question"
    # This creates a list where odd indices are headers and even indices are bodies
    parts = re.split(r'(^### question .*$)', content, flags=re.MULTILINE)

    final_output = [front_matter, CSS_BLOCK]

    # The first part (index 0) is the intro text (before first question)
    if parts[0].strip():
        final_output.append(parts[0].strip())

    # Process questions
    # Loop starts at 1 because 0 is intro. Step by 2 (header, body)
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i+1]

        # Cleanup <hr> tags that might be at the end of the body
        body = re.sub(r'<hr>\s*$', '', body.strip())

        # Identify where the options start. 
        # We look for the first occurrence of "1. " at the start of a line.
        list_match = re.search(r'(?m)^1\.\s', body)

        if list_match:
            question_text = body[:list_match.start()].strip()
            options_raw = body[list_match.start():]
            
            # Parse the numbered list into individual options
            # Split by "\n[digit]. "
            # We filter out empty strings resulting from split
            options_list = re.split(r'(?m)^\d+\.\s+', options_raw)
            options_list = [opt.strip() for opt in options_list if opt.strip()]

            # Construct the HTML structure
            q_html = f'\n<!-- {header.replace("### ", "").upper()} -->\n'
            q_html += f'<div class="quiz-block" markdown="1">\n'
            q_html += f'{header}\n\n'
            q_html += f'{question_text}\n\n'
            q_html += f'<ul class="quiz-options">\n'
            
            for opt in options_list:
                # Note: We do not add class="correct" here automatically 
                # because the script doesn't know the answer.
                # You must manually add class="option correct" to the right line.
                q_html += f'  <li class="option">{opt}</li>\n'
            
            q_html += f'</ul>\n'
            q_html += f'<div class="explanation">FIXME: Explanation for {header.replace("### ", "")}.</div>\n'
            q_html += f'</div>'

            final_output.append(q_html)
        else:
            # Fallback if format doesn't match expected structure
            final_output.append(header + "\n" + body)

    final_output.append(JS_BLOCK)
    
    return "\n<hr>".join(final_output)

if __name__ == "__main__":
    input_filename = sys.argv[1]
    output_filename = input_filename.split('.md')[0] + '_out.md'

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            raw_md = f.read()
        
        converted = convert_jekyll_quiz(raw_md)
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(converted)
            
        print(f"Successfully converted '{input_filename}' to '{output_filename}'")
        print("Don't forget to manually add the 'correct' class to the right answers in the output file!")
        
    except FileNotFoundError:
        print(f"Error: Could not find '{input_filename}'. Please create this file with your markdown content.")
