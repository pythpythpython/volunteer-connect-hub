# VolunteerConnect Hub

**AI-Powered Volunteering Planning, Outreach, Vetting, Coordinating, Organizing and Archiving Hub**

🔗 **Live Site**: [https://pythpythpython.github.io/volunteer-connect-hub/](https://pythpythpython.github.io/volunteer-connect-hub/)

---

## Overview

VolunteerConnect Hub is a comprehensive platform for volunteers of all types - students, professionals, families, and philanthropists. It combines AI-powered tools with real volunteer opportunities to help you make a meaningful impact in your community.

### Key Features

- 🔍 **Real Volunteer Opportunities** - Curated listings from VolunteerMatch, Habitat for Humanity, Red Cross, AmeriCorps, and more
- 📝 **Comprehensive User Profiles** - In-depth questionnaire that captures your skills, experience, interests, and availability
- 🎯 **Personalized Recommendations** - AI-powered matching based on your profile
- ✍️ **AI Letter Writer** - Generate professional application letters, thank you notes, and outreach emails
- 📅 **Schedule Management** - Track volunteer commitments with calendar export (iCal)
- ⏱️ **Hours Tracking** - Log volunteer hours, generate reports, and export data
- 💾 **Persistent Storage** - All data saved (localStorage or Supabase database)

---

## AGI Board System

This platform is powered by specialized AGI (Artificial General Intelligence) boards, each optimized for specific volunteering tasks:

| AGI Board | Purpose | Quality Target |
|-----------|---------|---------------|
| **User Profile AGI** | Comprehensive questionnaire and profile management | 100% |
| **Database AGI** | Secure data persistence with Supabase | 100% |
| **Opportunity Crawler AGI** | Fetches real volunteer opportunities | 100% |
| **Recommendation AGI** | Personalized opportunity matching | 100% |
| **Content Integrity AGI** | Ensures authentic content (no fake data) | 100% |
| **UX Testing AGI** | Automated testing and quality assurance | 100% |

---

## Getting Started

### For Users

1. Visit [the live site](https://pythpythpython.github.io/volunteer-connect-hub/)
2. Sign in (demo mode or Google OAuth)
3. **Complete your profile** (required) - This comprehensive questionnaire helps us:
   - Generate personalized opportunity recommendations
   - Create tailored application letters
   - Match you with opportunities that fit your skills and availability
4. Browse opportunities and start volunteering!

### For Developers

#### Local Development

```bash
# Clone the repository
git clone https://github.com/pythpythpython/volunteer-connect-hub.git
cd volunteer-connect-hub

# Install Ruby dependencies
bundle install

# Run Jekyll server
bundle exec jekyll serve

# Open http://localhost:4000/volunteer-connect-hub/
```

#### Setting Up Supabase (Production Database)

See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed instructions on:
- Creating a Supabase project
- Setting up Google OAuth
- Running the database schema
- Configuring environment variables

---

## Project Structure

```
volunteer-connect-hub/
├── _layouts/           # Jekyll page layouts
├── _data/              # YAML data files
├── assets/
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript (auth, database, app)
├── data/
│   └── opportunities.json  # Volunteer opportunities data
├── agi_boards/         # AGI Board implementations
│   ├── user_profile_board.py
│   ├── database_board.py
│   ├── opportunity_crawler_board.py
│   ├── recommendation_board.py
│   ├── content_board.py
│   └── ux_testing_board.py
├── .github/workflows/  # GitHub Actions
│   ├── deploy.yml
│   ├── ux-testing.yml
│   └── data-backup.yml
├── index.html          # Home page
├── opportunities.html  # Browse opportunities
├── schedule.html       # Schedule management
├── tracking.html       # Hours tracking
├── ai-assistant.html   # AI tools
├── onboarding.html     # Profile questionnaire
├── docs/               # Documentation
├── _config.yml         # Jekyll configuration
└── README.md
```

---

## User Profile Questionnaire

The profile questionnaire is **required** to use the platform. It collects:

1. **Personal Information** - Name, location, age group, volunteer type
2. **Skills & Expertise** - Professional skills, languages, certifications
3. **Education & Work** - Background for context in applications
4. **Volunteer Experience** - Previous volunteering history
5. **Interests & Causes** - What you're passionate about
6. **Availability** - When and how you can volunteer
7. **Goals & Motivation** - Why you want to volunteer

This data is used to:
- Generate personalized opportunity recommendations
- Create tailored application letters
- Match you with the right organizations
- Track your volunteer journey

---

## Data Storage

### Demo Mode (Default)
- All data stored in browser localStorage
- No server required
- Data persists until browser data is cleared

### Production Mode (Supabase)
- Full PostgreSQL database
- Google OAuth authentication
- Row-level security for data protection
- Automatic profile creation on signup
- Data backup to GitHub repo

---

## Opportunity Sources

Real volunteer opportunities are aggregated from:

- **VolunteerMatch** - volunteermatch.org
- **Idealist** - idealist.org
- **Habitat for Humanity** - habitat.org
- **American Red Cross** - redcross.org
- **AmeriCorps** - americorps.gov
- **Feeding America** - feedingamerica.org

Data is updated periodically via GitHub Actions.

---

## Testing & Quality Assurance

### Automated Testing
- **UX Testing AGI Board** runs checks on every push
- Tests verify all pages load, links work, and content is authentic
- GitHub Actions workflow runs daily

### Run Tests Locally
```bash
cd volunteer-connect-hub
python3 agi_boards/ux_testing_board.py
```

### Content Integrity
- No fake testimonials or statistics
- All data is either user-generated or clearly labeled as examples
- Content Integrity AGI Board enforces these rules

---

## API Integration (Advanced)

For automated improvements and new module development:

```yaml
# .github/workflows/cursor-integration.yml
# Integrates with Cursor API for AI-powered enhancements
CURSOR_API_KEY: key_0ea8355199c5ac7addf66d283861cab2ea6ec4497e7adb6783f8292ea081ff9b
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run UX tests to verify
5. Submit a pull request

### Code of Conduct
- All contributions must maintain 100% quality target
- No fake content or testimonials
- Follow existing code style and conventions

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/pythpythpython/volunteer-connect-hub/issues)
- **Documentation**: [Docs Page](https://pythpythpython.github.io/volunteer-connect-hub/docs/)

---

Built with ❤️ by the VolunteerConnect AGI Team
