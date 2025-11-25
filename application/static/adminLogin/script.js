document.addEventListener('DOMContentLoaded', function() {
    // Toggle password visibility
    const togglePassword = document.querySelector('.toggle-password');
    const password = document.getElementById('password');
    
    if (togglePassword && password) {
        togglePassword.addEventListener('click', function() {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }
    
    // Form validation
    const form = document.getElementById('loginForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
            
            if (form.checkValidity()) {
                event.preventDefault();
                // Here you would typically send the data to the server
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const remember = document.getElementById('remember').checked;
                
                console.log('Login attempt with:', { email, password, remember });
                
                // Simulate loading
                const submitBtn = form.querySelector('button[type="submit"]');
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> جاري التحقق...';
                submitBtn.disabled = true;
                
                // Simulate API call
                setTimeout(() => {
                    submitBtn.innerHTML = 'تسجيل الدخول';
                    submitBtn.disabled = false;
                    
                    // Show success message (in a real app, you'd check the response)
                    alert('تم تسجيل الدخول بنجاح!');
                }, 2000);
            }
        }, false);
    }
    
    // Social login buttons
    const socialButtons = document.querySelectorAll('.social-btn');
    socialButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const platform = this.querySelector('i').classList[1].split('-')[1];
            alert(`سيتم توجيهك إلى ${platform} للمصادقة`);
        });
    });
});