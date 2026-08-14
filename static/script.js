document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('voteForm');
  if(form){
    form.addEventListener('submit', function(e){
      const btn = document.getElementById('submitBtn');
      if(btn){
        btn.disabled = true;
        btn.textContent = 'Submitting...';
      }
    });
  }
  
  // Admin: dynamic add option fields
  const addOptBtn = document.getElementById('addOptionBtn');
  const optionsContainer = document.getElementById('options-container');
  if(addOptBtn && optionsContainer){
    addOptBtn.addEventListener('click', function(){
      const count = optionsContainer.querySelectorAll('.option-input').length + 1;
      if(count > 20) return; // limit
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'options';
      input.placeholder = 'Option ' + count;
      input.className = 'option-input';
      optionsContainer.appendChild(input);
      input.focus();
    });
  }
});
