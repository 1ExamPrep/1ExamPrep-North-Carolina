"""Blog posts for passyournorthcarolinacontractorexam.com. Facts checked Nov 24, 2026 against the NC General Statutes,
the NC Administrative Code, nclicensing.org and NASCLA."""

AUTHOR = "Max Ace"

BSRC = {}

POSTS = [dict(
    slug="north-carolina-contractor-license-questions-answered",
    title="North Carolina Contractor License: 15 Questions Answered",
    meta_title="NC Contractor License: 15 Questions Answered (2026)",
    meta_desc="Straight answers to the 15 most-asked North Carolina contractor license questions: which board, the $40,000 rule, exams, limits, HVAC groups and NASCLA.",
    date="2026-11-24", updated="2026-11-24",
    excerpt="Which of the three boards licenses you, the $40,000 rule, NCLBGC limitations, electrical caps, Heating Groups 1 to 3 and the NASCLA route, answered in plain English.",
    tags=["Licensing", "Exams", "North Carolina"],
    lead=("North Carolina contractors are licensed by three separate boards. General contractors need an NCLBGC license for projects of $40,000 or more, "
          "electrical contractors answer to the electrical board, and plumbing, HVAC and fire sprinkler contractors to the Plumbing Board. "
          "Here are straight answers to the 15 questions people ask most."),
    takeaways=["General contractor license needed for projects of $40,000 or more (G.S. 87-1).", "NCLBGC limitations: $750,000, $1,500,000 or unlimited per project.",
               "NCLBGC trade and Business and Law exams: 70% to pass, open book.", "Electrical caps: $100,000 Limited, $200,000 Intermediate by statute.",
               "Heating Group 2 is over 15 tons; Group 3 is forced air of 15 tons or less."],
    sections=[
        ("do-you-need-a-license", "Do you need a contractor license in North Carolina?",
         "<p>Yes, once a job crosses the line for your trade. Under G.S. 87-1, anyone who undertakes to build a building, highway, public utility, grading or other improvement where the cost is $40,000 or more is a general contractor and needs a license from the North Carolina Licensing Board for General Contractors (NCLBGC). "
         "The trades work differently. Electrical contracting needs a license from the State Board of Examiners of Electrical Contractors, and plumbing, heating and fire sprinkler work needs a license from the State Board of Examiners of Plumbing, Heating and Fire Sprinkler Contractors. "
         "Those trade licenses apply on small jobs too, so a $5,000 panel change still needs a licensed electrical contractor.</p>"),
        ("under-40000", "How much work can you do without a general contractor license?",
         "<p>Up to, but not including, $40,000 per project. The threshold covers the whole cost of the undertaking, labor and materials together, and a project cannot be split into smaller contracts to stay under it. "
         "The threshold was $30,000 before the General Assembly raised it, so guides that still quote $30,000 are out of date. "
         "Staying under $40,000 only removes the NCLBGC requirement. Local permits still apply, and any electrical, plumbing or HVAC work still needs a licensed trade contractor.</p>"),
        ("three-boards", "What is the difference between the three North Carolina boards?",
         "<p>Each board was set up by its own article of Chapter 87 of the General Statutes and runs its own applications, exams and renewals.</p>"
         "<table><thead><tr><th></th><th>NCLBGC</th><th>Electrical board</th><th>Plumbing Board</th></tr></thead><tbody>"
         "<tr><td>Statute</td><td>Chapter 87, Article 1</td><td>Chapter 87, Article 4</td><td>Chapter 87, Article 2</td></tr>"
         "<tr><td>Work covered</td><td>Building, residential, highway, utilities, specialty</td><td>Electrical contracting</td><td>Plumbing, HVAC, fuel piping, fire sprinkler</td></tr>"
         "<tr><td>Trigger</td><td>Projects of $40,000 or more</td><td>Any electrical contracting</td><td>Any plumbing, heating or sprinkler contracting</td></tr>"
         "<tr><td>Tiers</td><td>Limited, Intermediate, Unlimited</td><td>Limited, Intermediate, Unlimited, SP</td><td>Class I, Class II, groups and technicians</td></tr>"
         "<tr><td>Exams</td><td>PSI trade plus Business and Law</td><td>Board written exam or NASCLA route</td><td>Board exam at 7 testing centers</td></tr></tbody></table>"
         "<p>A general contractor license never covers the trade work itself. A builder who wires a house still needs an electrical license.</p>"),
        ("classifications", "Which NCLBGC classification should you choose?",
         "<p>Pick the classification that matches the work you bid. Building is the broadest and covers commercial, industrial, institutional and residential buildings of all types. "
         "Residential covers homes built under the North Carolina Residential Code. Highway covers roads, bridges and paving, and Public Utilities covers water, sewer, fuel distribution and communication lines, with subclassifications such as Water Lines and Sewer Lines. "
         "Specialty classifications cover single trades such as Roofing, Masonry, Concrete Construction, Insulation, Interior Construction, Metal Erection and Swimming Pools. "
         "A license can carry more than one classification, and each one needs its own trade exam.</p>"),
        ("limitations", "How big a job can you bid with an NCLBGC license?",
         "<p>The limitation decides it. It caps the value of any single project, not your yearly revenue. G.S. 87-10 sets the tiers, and 21 NCAC 12A .0204 sets the financial test.</p>"
         "<table><thead><tr><th>Limitation</th><th>Single project limit</th><th>Working capital</th><th>Bond alternative</th><th>Application fee</th></tr></thead><tbody>"
         "<tr><td>Limited</td><td>$750,000</td><td>$17,000</td><td>$175,000</td><td>$75</td></tr>"
         "<tr><td>Intermediate</td><td>$1,500,000</td><td>$75,000</td><td>$500,000</td><td>$100</td></tr>"
         "<tr><td>Unlimited</td><td>No limit</td><td>$150,000</td><td>$1,000,000</td><td>$125</td></tr></tbody></table>"
         "<p>The cost of land and ancillary site improvements is left out of the project value. A contractor doing many small jobs can stay Limited; one $800,000 job needs Intermediate.</p>"),
        ("nclbgc-exams", "What exams does the NCLBGC require?",
         "<p>Two, for most applicants. The qualifier passes a trade exam for each classification and the North Carolina Business and Law exam, both given by PSI. "
         "Each needs a score of 70 percent, and both are open book with the approved references, so the edition of each book matters. "
         "The Business and Law exam is built on the NASCLA Contractor's Guide to Business, Law and Project Management, NC General edition, and the Board's book of laws and regulations. "
         "Most candidates spend 4 to 8 weeks on the two exams together.</p>"),
        ("nascla", "Does North Carolina accept the NASCLA exam?",
         "<p>Yes, in two places. The NCLBGC accepts the NASCLA Commercial General Building exam in place of its Building trade exam, although the North Carolina Business and Law exam is still required. "
         "The electrical board accepts the NASCLA Electrical Contractor exam as an alternative to its own qualifying exam, as long as the candidate also scores at least 18 of 25 on the North Carolina Laws, Rules and Business Practices test under 21 NCAC 18B .0212. "
         "The electrical board also accepts the NASCLA Residential Electrical Contractor exam in place of its SP-SFD exam. "
         "A NASCLA score is portable, which helps contractors who work in several states.</p>"),
        ("electrical-classes", "How do North Carolina electrical licenses work?",
         "<p>G.S. 87-43.3 sets three classes plus special restricted classes. A Limited license covers single projects up to the value the Board sets, which the statute caps at $100,000, on installations rated 1,000 volts or less. "
         "An Intermediate license covers single projects up to a Board-set value capped at $200,000. An Unlimited license covers any project, regardless of value. "
         "Special restricted (SP) classes cover one phase of work, such as SP-SFD for single-family detached homes, SP-FA/LV for fire alarm and low voltage, SP-PH for plumbing and heating equipment wiring and SP-SP for swimming pool bonding. "
         "Limited and SP applicants need no more than 3,000 hours of experience, and Intermediate applicants no more than 5,750 hours.</p>"),
        ("journeyman", "Is there a statewide journeyman electrician license in North Carolina?",
         "<p>No. The State Board of Examiners of Electrical Contractors licenses electrical contracting businesses through a qualified individual, not individual journeymen. "
         "Journeyman and master credentials for workers depend on the employer or the local program, so ask which National Electrical Code edition your exam uses. "
         "Most current study material is built on the 2026 or 2023 NEC. When you are ready to contract on your own, you move up to the Limited, Intermediate or Unlimited contractor exam.</p>"),
        ("plumbing-classes", "What do Plumbing Class I and Class II cover?",
         "<p>G.S. 87-21 sets two classes. Class I covers plumbing, heating and fire sprinkler systems for all structures, and Class II covers plumbing and heating systems in single-family detached residential dwellings. "
         "Most commercial plumbers hold Class I, and most residential plumbers start with Class II. The Board also licenses plumbing technicians and a Restricted Limited Plumbing contractor for a narrow scope of work. "
         "Contractor applicants need 2 years (4,000 hours) of experience, and up to 2,000 of those hours can be academic or technical training.</p>"),
        ("heating-groups", "What is the difference between Heating Groups 1, 2 and 3?",
         "<p>The Plumbing Board splits HVAC licensing by system type. Heating Group 1 covers hydronic heating systems, such as boilers and hot-water piping. "
         "Heating Group 2 covers the installation and replacement of air conditioning systems greater than 15 tons. Heating Group 3 covers forced-air heating and cooling systems of 15 tons or less. "
         "Groups 1 and 3 come in Class I for any building and Class II for single-family detached homes. Most residential HVAC contractors start with Heating Group 3 Class II, and many add SP-PH from the electrical board to wire their own equipment.</p>"),
        ("plumbing-board-exams", "How do Plumbing Board exams work?",
         "<p>The Board approves your application first, then sends a notice. You must take the exam within 90 days of the notification date, and exams run daily at 7 testing centers: Asheville, Charlotte, Winston-Salem, Raleigh, Fayetteville, Greenville and Wilmington. "
         "You bring the allowed reference materials yourself, and they are checked against the Board's Book Reference List at the door. "
         "Pass or fail is reported at the testing center. A failed exam means a 90-day wait before retesting, and the Board offers an exam review in Raleigh.</p>"),
        ("fire-sprinkler-fuel", "Who licenses fuel piping and fire sprinkler contractors?",
         "<p>The Plumbing Board licenses both. A Fuel Piping Contractor needs 1 year (2,000 hours) of experience, up to 1,000 hours of which can be training, and a Fuel Piping Technician needs 9 months (1,500 hours). "
         "A Fire Sprinkler Installation Contractor needs a current NICET Level III certificate in automatic sprinkler system layout and must pass the business and law part of the Board exam. "
         "The Board also licenses fire sprinkler inspection contractors and technicians, each with its own certification or experience rule.</p>"),
        ("how-long", "How long does it take to get licensed?",
         "<p>Plan on 2 to 4 months from first study session to license in hand. Most candidates study 4 to 8 weeks, and the board review adds time before and after the exam. "
         "The Plumbing Board's 90-day exam window and the NCLBGC's financial review are the usual places where time goes. "
         "A simple study plan: 2 weeks learning the layout of each reference book, 2 to 4 weeks of practice questions, and 1 to 2 weeks of timed full exams.</p>"),
        ("cost", "How much does a North Carolina contractor license cost?",
         "<p>Expect a few hundred dollars in fees plus study materials. The NCLBGC application fee is $75 for Limited, $100 for Intermediate and $125 for Unlimited, plus PSI exam fees and the cost of meeting the working capital test or a bond. "
         "Study materials range from about $80 for an online practice test to $3,000 or more for a complete highlighted and tabbed book set with a course. "
         "Every <a href='/licenses/'>license page</a> on this site lists every package and price, and the <a href='/how-to-get-licensed/'>licensing guide</a> walks through each step.</p>"),
    ],
    faq=[
        ("When do I need a North Carolina general contractor license?", "When a project costs $40,000 or more, under G.S. 87-1."),
        ("What score passes the NCLBGC exams?", "70 percent on the trade exam and on the Business and Law exam."),
        ("What are the NCLBGC limitations?", "Limited up to $750,000, Intermediate up to $1,500,000 and Unlimited with no limit, per single project."),
        ("Is the NASCLA exam accepted in North Carolina?", "Yes, for the NCLBGC Building classification and, with an 18 of 25 rules test, for electrical contractors."),
        ("Which board licenses HVAC contractors?", "The State Board of Examiners of Plumbing, Heating and Fire Sprinkler Contractors, through Heating Groups 1, 2 and 3."),
        ("What is the Heating Group 2 tonnage line?", "Heating Group 2 covers air conditioning systems greater than 15 tons."),
        ("Where does the Plumbing Board test?", "Asheville, Charlotte, Winston-Salem, Raleigh, Fayetteville, Greenville and Wilmington, every day."),
        ("How do I get help choosing exam prep?", "Call (877) 775-9400 or email sales@1examprep.com with your license and exam date."),
    ],
    sources=["gs87_1", "gs87_10", "ncac12a", "gs87_43", "ncac18b", "nascla_el", "gs87_21", "plb_app"],
)]
