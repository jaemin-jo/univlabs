// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    navToggle.addEventListener('click', function() {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active');
        });
    });

    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Active navigation link highlighting
    window.addEventListener('scroll', function() {
        let current = '';
        const sections = document.querySelectorAll('section');
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
});

// Initialize AOS (Animate On Scroll)
document.addEventListener('DOMContentLoaded', function() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000,
            once: true,
            offset: 100
        });
    }
});

// Form submission handling
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.querySelector('.form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const name = formData.get('name');
            const email = formData.get('email');
            const subject = formData.get('subject');
            const message = formData.get('message');
            
            // Simple validation
            if (!name || !email || !subject || !message) {
                showNotification('모든 필드를 입력해주세요.', 'error');
                return;
            }
            
            if (!isValidEmail(email)) {
                showNotification('올바른 이메일 주소를 입력해주세요.', 'error');
                return;
            }
            
            // Simulate form submission
            const submitBtn = this.querySelector('.submit-btn');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<span>전송 중...</span>';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                showNotification('메시지가 성공적으로 전송되었습니다!', 'success');
                this.reset();
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
});

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#6366f1'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 400px;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Parallax effect for floating elements
document.addEventListener('DOMContentLoaded', function() {
    const floatingElements = document.querySelectorAll('.floating-element');
    
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        floatingElements.forEach((element, index) => {
            const speed = (index + 1) * 0.1;
            element.style.transform = `translateY(${rate * speed}px)`;
        });
    });
});

// Intersection Observer for animations
document.addEventListener('DOMContentLoaded', function() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe elements with fade-in class
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        observer.observe(element);
    });
});

// Enhanced phone mockup interaction with mouse tracking
document.addEventListener('DOMContentLoaded', function() {
    const phoneMockups = document.querySelectorAll('.phone-mockup, .showcase-phone');
    
    phoneMockups.forEach(mockup => {
        let isHovering = false;
        
        mockup.addEventListener('mouseenter', function() {
            isHovering = true;
        });
        
        mockup.addEventListener('mouseleave', function() {
            isHovering = false;
            if (this.classList.contains('phone-mockup')) {
                this.style.transform = 'perspective(1000px) rotateY(-15deg) rotateX(5deg)';
            } else {
                this.style.transform = 'perspective(1000px) rotateY(15deg) rotateX(-5deg)';
            }
        });
        
        mockup.addEventListener('mousemove', function(e) {
            if (!isHovering) return;
            
            const rect = this.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            const mouseX = e.clientX - centerX;
            const mouseY = e.clientY - centerY;
            
            const rotateX = (mouseY / rect.height) * 20;
            const rotateY = (mouseX / rect.width) * 20;
            
            if (this.classList.contains('phone-mockup')) {
                this.style.transform = `perspective(1000px) rotateY(${-15 + rotateY}deg) rotateX(${5 - rotateX}deg) translateY(-10px)`;
            } else {
                this.style.transform = `perspective(1000px) rotateY(${15 + rotateY}deg) rotateX(${-5 - rotateX}deg) translateY(-10px)`;
            }
        });
    });
});

// Download button interactions
document.addEventListener('DOMContentLoaded', function() {
    const downloadBtns = document.querySelectorAll('.download-btn');
    
    downloadBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Add click animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
            
            // Show coming soon message for iOS
            if (this.classList.contains('ios')) {
                showNotification('iOS 버전은 곧 출시 예정입니다!', 'info');
            } else {
                showNotification('Android 버전 다운로드를 준비 중입니다...', 'info');
            }
        });
    });
});

// Feature cards hover effects
document.addEventListener('DOMContentLoaded', function() {
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Smooth reveal animations for sections
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('section');
    
    const sectionObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('section-visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    });
    
    sections.forEach(section => {
        sectionObserver.observe(section);
    });
});

// Enhanced scroll animations and effects
document.addEventListener('DOMContentLoaded', function() {
    // Parallax scrolling for floating elements
    const floatingElements = document.querySelectorAll('.floating-element');
    
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        floatingElements.forEach((element, index) => {
            const speed = (index + 1) * 0.1;
            const yPos = rate * speed;
            const xPos = Math.sin(scrolled * 0.001 + index) * 10;
            element.style.transform = `translate(${xPos}px, ${yPos}px) rotate(${scrolled * 0.1}deg)`;
        });
    });
    
    // Enhanced feature card animations
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.03)';
            this.style.boxShadow = '0 25px 50px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.05)';
        });
    });
    
    // Company card enhanced animations
    const companyCards = document.querySelectorAll('.company-card');
    
    companyCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.05) rotateY(5deg)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1) rotateY(0deg)';
        });
    });
    
    // Assignment item animations
    const assignmentItems = document.querySelectorAll('.assignment-item');
    
    assignmentItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px) scale(1.02)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0) scale(1)';
        });
    });
});

// Add CSS for enhanced animations
const style = document.createElement('style');
style.textContent = `
    section {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.8s ease;
    }
    
    section.section-visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    }
    
    .nav-link.active {
        color: #6366f1;
    }
    
    .nav-link.active::after {
        width: 100%;
    }
    
    /* Enhanced scroll animations */
    .feature-card {
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .company-card {
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .assignment-item {
        animation: slideInFromLeft 0.6s ease forwards;
        opacity: 0;
        transform: translateX(-20px);
    }
    
    @keyframes slideInFromLeft {
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Enhanced phone mockup effects */
    .phone-mockup {
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .showcase-phone {
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Floating elements enhanced animation */
    .floating-element {
        transition: all 0.3s ease;
    }
    
    /* AI icon glow effect */
    .ai-icon {
        position: relative;
    }
    
    .ai-icon::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        border-radius: 18px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
        filter: blur(4px);
    }
    
    .ai-icon:hover::before {
        opacity: 0.7;
    }
`;
document.head.appendChild(style);
