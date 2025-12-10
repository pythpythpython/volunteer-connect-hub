/**
 * VolunteerConnect Hub - Main Application JavaScript
 * ==================================================
 * AI-powered volunteering management system
 */

// Application State
const AppState = {
    user: null,
    volunteers: [],
    opportunities: [],
    schedule: [],
    hours: [],
    currentPage: 'home'
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initModals();
    loadAppState();
    initServiceWorker();
});

// Navigation
function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
    
    // Close menu on link click
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navMenu?.classList.remove('active');
        });
    });
}

// Modal Management
function initModals() {
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.getAttribute('data-modal');
            openModal(modalId);
        });
    });
    
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal-overlay');
            closeModal(modal);
        });
    });
    
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal(overlay);
            }
        });
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modal) {
    if (typeof modal === 'string') {
        modal = document.getElementById(modal);
    }
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Local Storage Management
function loadAppState() {
    const savedState = localStorage.getItem('volunteerConnectState');
    if (savedState) {
        try {
            const parsed = JSON.parse(savedState);
            Object.assign(AppState, parsed);
        } catch (e) {
            console.error('Failed to load app state:', e);
        }
    }
}

function saveAppState() {
    try {
        localStorage.setItem('volunteerConnectState', JSON.stringify(AppState));
    } catch (e) {
        console.error('Failed to save app state:', e);
    }
}

// Volunteer Management
const VolunteerManager = {
    async trackOutreach(contact) {
        const outreach = {
            id: generateId(),
            contact,
            date: new Date().toISOString(),
            status: 'contacted',
            followUpDate: null,
            notes: ''
        };
        
        AppState.volunteers.push(outreach);
        saveAppState();
        
        return outreach;
    },
    
    async updateStatus(id, status, notes = '') {
        const volunteer = AppState.volunteers.find(v => v.id === id);
        if (volunteer) {
            volunteer.status = status;
            volunteer.notes = notes;
            volunteer.lastUpdated = new Date().toISOString();
            saveAppState();
        }
        return volunteer;
    },
    
    getAll() {
        return AppState.volunteers;
    },
    
    getByStatus(status) {
        return AppState.volunteers.filter(v => v.status === status);
    }
};

// Schedule Management
const ScheduleManager = {
    async addEvent(event) {
        const scheduleItem = {
            id: generateId(),
            ...event,
            created: new Date().toISOString(),
            reminders: []
        };
        
        AppState.schedule.push(scheduleItem);
        saveAppState();
        
        // Schedule reminders
        if (event.sendReminders) {
            await this.scheduleReminder(scheduleItem);
        }
        
        return scheduleItem;
    },
    
    async scheduleReminder(event) {
        // Store reminder for later processing
        event.reminders.push({
            type: 'email',
            scheduledFor: new Date(new Date(event.date).getTime() - 24 * 60 * 60 * 1000).toISOString(),
            sent: false
        });
        saveAppState();
    },
    
    getUpcoming(days = 7) {
        const now = new Date();
        const future = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
        
        return AppState.schedule.filter(event => {
            const eventDate = new Date(event.date);
            return eventDate >= now && eventDate <= future;
        }).sort((a, b) => new Date(a.date) - new Date(b.date));
    },
    
    exportToICS() {
        let ics = 'BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//VolunteerConnect//EN\n';
        
        AppState.schedule.forEach(event => {
            ics += 'BEGIN:VEVENT\n';
            ics += `UID:${event.id}@volunteerconnect\n`;
            ics += `DTSTART:${formatDateForICS(event.date)}\n`;
            ics += `SUMMARY:${event.title}\n`;
            ics += `DESCRIPTION:${event.description || ''}\n`;
            ics += `LOCATION:${event.location || ''}\n`;
            ics += 'END:VEVENT\n';
        });
        
        ics += 'END:VCALENDAR';
        
        const blob = new Blob([ics], { type: 'text/calendar' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'volunteer-schedule.ics';
        a.click();
        
        URL.revokeObjectURL(url);
    }
};

// Hours Tracking
const HoursTracker = {
    async logHours(entry) {
        const hoursEntry = {
            id: generateId(),
            ...entry,
            logged: new Date().toISOString(),
            verified: false
        };
        
        AppState.hours.push(hoursEntry);
        saveAppState();
        
        return hoursEntry;
    },
    
    getTotalHours(period = 'all') {
        let hours = AppState.hours;
        
        if (period !== 'all') {
            const now = new Date();
            let startDate;
            
            switch (period) {
                case 'week':
                    startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    break;
                case 'month':
                    startDate = new Date(now.getFullYear(), now.getMonth(), 1);
                    break;
                case 'year':
                    startDate = new Date(now.getFullYear(), 0, 1);
                    break;
            }
            
            hours = hours.filter(h => new Date(h.date) >= startDate);
        }
        
        return hours.reduce((total, entry) => total + (entry.hours || 0), 0);
    },
    
    getByOpportunity(opportunityId) {
        return AppState.hours.filter(h => h.opportunityId === opportunityId);
    },
    
    generateReport(period = 'month') {
        const hours = this.getTotalHours(period);
        const entries = AppState.hours.filter(h => {
            const date = new Date(h.date);
            const now = new Date();
            
            if (period === 'month') {
                return date.getMonth() === now.getMonth() && 
                       date.getFullYear() === now.getFullYear();
            }
            return true;
        });
        
        return {
            totalHours: hours,
            entriesCount: entries.length,
            averagePerEntry: entries.length > 0 ? hours / entries.length : 0,
            byOrganization: this.groupByOrganization(entries)
        };
    },
    
    groupByOrganization(entries) {
        const grouped = {};
        entries.forEach(entry => {
            const org = entry.organization || 'Unspecified';
            if (!grouped[org]) {
                grouped[org] = { hours: 0, count: 0 };
            }
            grouped[org].hours += entry.hours || 0;
            grouped[org].count += 1;
        });
        return grouped;
    }
};

// AI Assistant Interface
const AIAssistant = {
    async generateLetter(type, context) {
        // This would call the backend AGI service
        const prompt = this.buildPrompt(type, context);
        
        // For demo purposes, return a template
        const templates = {
            application: this.getApplicationTemplate(context),
            thankyou: this.getThankYouTemplate(context),
            outreach: this.getOutreachTemplate(context),
            followup: this.getFollowUpTemplate(context)
        };
        
        return templates[type] || templates.application;
    },
    
    buildPrompt(type, context) {
        return `Generate a ${type} letter for volunteering with the following context: ${JSON.stringify(context)}`;
    },
    
    getApplicationTemplate(ctx) {
        return `Dear ${ctx.recipientName || 'Hiring Manager'},

I am writing to express my interest in volunteering with ${ctx.organization || 'your organization'}. ${ctx.reason || 'I am passionate about making a positive impact in my community.'}

${ctx.experience ? `I have experience in: ${ctx.experience}` : ''}

I am available ${ctx.availability || 'on weekends and evenings'} and am committed to contributing ${ctx.hours || 'several hours'} per week.

${ctx.skills ? `My relevant skills include: ${ctx.skills}` : ''}

Thank you for considering my application. I look forward to the opportunity to contribute to your mission.

Sincerely,
${ctx.senderName || '[Your Name]'}`;
    },
    
    getThankYouTemplate(ctx) {
        return `Dear ${ctx.recipientName || 'Team'},

I wanted to express my heartfelt gratitude for the opportunity to volunteer with ${ctx.organization || 'your organization'}.

${ctx.experience || 'The experience has been incredibly rewarding.'} ${ctx.impact || ''}

Thank you for your guidance and support throughout my time volunteering.

With appreciation,
${ctx.senderName || '[Your Name]'}`;
    },
    
    getOutreachTemplate(ctx) {
        return `Subject: Partnership Opportunity - Volunteer Program

Dear ${ctx.recipientName || 'Community Partner'},

I am reaching out on behalf of ${ctx.organization || 'our volunteer program'} to explore potential collaboration opportunities.

${ctx.purpose || 'We are looking to expand our volunteer initiatives and believe your organization would be an excellent partner.'}

${ctx.benefits || 'Together, we could make a significant impact in our community.'}

Would you be available for a brief call to discuss this further?

Best regards,
${ctx.senderName || '[Your Name]'}`;
    },
    
    getFollowUpTemplate(ctx) {
        return `Dear ${ctx.recipientName || 'Volunteer Coordinator'},

I hope this message finds you well. I am following up on my ${ctx.previousAction || 'previous application/inquiry'} regarding volunteer opportunities with ${ctx.organization || 'your organization'}.

${ctx.additionalInfo || 'I remain very interested in contributing to your mission.'}

Please let me know if there are any updates or if you need any additional information from me.

Thank you for your time.

Best regards,
${ctx.senderName || '[Your Name]'}`;
    },
    
    async fillFormFromScreenshot(imageData) {
        // This would use OCR and AI to extract form fields
        // For demo, return placeholder
        return {
            detected: true,
            fields: [
                { name: 'name', value: AppState.user?.name || '' },
                { name: 'email', value: AppState.user?.email || '' },
                { name: 'phone', value: '' },
                { name: 'availability', value: '' }
            ],
            confidence: 0.85,
            requiresReview: true
        };
    },
    
    async answerQuestion(question, context) {
        // This would use the AGI to answer volunteer-related questions
        const commonQuestions = {
            'availability': 'Based on your schedule, you are available on weekends.',
            'experience': 'You have volunteered for a total of ' + HoursTracker.getTotalHours() + ' hours.',
            'next': 'Your next scheduled volunteer activity is ' + (ScheduleManager.getUpcoming(1)[0]?.title || 'not yet scheduled.')
        };
        
        for (const [key, answer] of Object.entries(commonQuestions)) {
            if (question.toLowerCase().includes(key)) {
                return answer;
            }
        }
        
        return 'I can help you with volunteer scheduling, hours tracking, letter writing, and more. What would you like to know?';
    }
};

// Form Auto-Fill
const FormFiller = {
    async processScreenshot(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                const imageData = e.target.result;
                const result = await AIAssistant.fillFormFromScreenshot(imageData);
                resolve(result);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    },
    
    async autoFillForm(formElement, data) {
        const inputs = formElement.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            const name = input.name || input.id;
            if (data[name]) {
                input.value = data[name];
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
    }
};

// Utility Functions
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function formatDateForICS(date) {
    const d = new Date(date);
    return d.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
}

function formatDate(date, options = {}) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        ...options
    });
}

function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Notification System
const NotificationManager = {
    async requestPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return false;
    },
    
    async send(title, body, options = {}) {
        if (Notification.permission === 'granted') {
            new Notification(title, {
                body,
                icon: '/assets/images/icon.png',
                ...options
            });
        }
    },
    
    async scheduleReminder(event, minutesBefore = 60) {
        const eventTime = new Date(event.date).getTime();
        const reminderTime = eventTime - minutesBefore * 60 * 1000;
        const now = Date.now();
        
        if (reminderTime > now) {
            setTimeout(() => {
                this.send(
                    'Upcoming Volunteer Event',
                    `${event.title} starts in ${minutesBefore} minutes`,
                    { tag: event.id }
                );
            }, reminderTime - now);
        }
    }
};

// Service Worker Registration
function initServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('ServiceWorker registered:', registration.scope);
            })
            .catch(err => {
                console.log('ServiceWorker registration failed:', err);
            });
    }
}

// Export for use in other scripts
window.VolunteerConnect = {
    AppState,
    VolunteerManager,
    ScheduleManager,
    HoursTracker,
    AIAssistant,
    FormFiller,
    NotificationManager,
    openModal,
    closeModal,
    formatDate,
    formatTime
};
