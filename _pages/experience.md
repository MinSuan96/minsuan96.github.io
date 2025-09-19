---
layout: page
title: experiences
permalink: /experiences/
description: Here's where I talk about my experiences.
nav: true
nav_order: 2
---

# InsiderSecurity

| Job Title: |     | Software Engineer                              |
| ---------- | --- | ---------------------------------------------- |
| Company:   |     | [InsiderSecurity](https://insidersecurity.co/) |
| Location:  |     | Kuala Lumpur, Malaysia                         |
| Date:      |     | 06<sup>th</sup> May 2024 - Present             |

<br>

InsiderSecurity's [Automated User and Entity Behavior Analytics (UEBA)](https://insidersecurity.co/products/automated-user-and-entity-behaviour-analytics/) detects malicious user activity within both on-premise and cloud infrastructures. It leverages machine learning and advanced behavior analytics to identify threats like hijacked accounts, insider data theft, and compromised servers. Automated UEBA provides early detection, enabling timely action to prevent data loss. It is designed to be highly automated, reducing the need for large IT security teams, and is deployed by large enterprises and governments.

### Job Scope

As a Software Engineer, I played a critical role in optimizing backend systems and enhancing the performance and scalability of Automated UEBA. My contributions spanned across automation, risk model improvements, and system integrations, ensuring high availability, security, and compliance with industry standards.

#### Risk Model Optimization and Scalability

Single-handedly led efforts to optimize the core risk scoring engine, improving its ability to process high volumes of alert data efficiently by implementing multiprocessing, streamlining code, and redesigning the caching mechanism. [This resulted in at least a 140% improvement in performance.](https://minsuan96.github.io/assets/pdf/BNWEngineV4_Results.pdf)

#### Integration with Cloud Infrastructures

Integrated the product with various cloud infrastructures, including Amazon Web Services (AWS) and Microsoft Azure, enhancing its capability to monitor and analyze activities across diverse environments. Traditionally, the product was designed to work with on-premise systems, but with the growing adoption of cloud services, this integration was crucial for comprehensive security monitoring. Many of the customers of InsiderSecurity have to comply with regulations that require monitoring of cloud activities, and in order to use the product, [it has to used under the GCC environment](https://www.tech.gov.sg/products-and-services/for-government-agencies/software-development/government-on-commercial-cloud), making this integration a key requirement.

#### Sensorless Pipeline Development

As mentioned, more and more customers are moving to the cloud, and some of them are sending logs directly from their systems. To cater to these customers, I developed a sensorless pipeline that allows the product to collect and analyze logs directly from cloud services and syslog without the need for on-premise sensors. This not only involved receiving logs from cloud services but also ensuring that the logs were processed and analyzed in a way that was consistent with the existing system. This development was crucial for expanding the product's market reach and ensuring that it could meet the needs of customers.

#### Sensor Improvements and Feature Enhancements

Enhanced sensor capabilities by adding new features, such as support for additional log formats, auditing capabilities, log rotation, additional capability of receiving commands from the backend, bug fixes and more. The sensor is written in C++ and is responsible for collecting and forwarding log data to the backend system. These improvements not only increased the sensor's functionality but also improved its reliability and performance in diverse environments.

#### Automation of Sensor Role and Tag Assignment

Developed automated systems for the role and tag assignment of sensors, reducing manual intervention and improving the accuracy of sensor data processing. This automation streamlined the deployment and management of sensors across various environments, ensuring that they were correctly configured to meet specific monitoring requirements. This was particularly important as the number of sensors deployed increased, making manual configuration impractical. The automation system utilized Redis for caching and identification of sensors, ensuring efficient and accurate role and tag assignments.

#### Forwarder System Enhancement

One of the key features of the product is its ability to forward logs to third-party systems and other log management solutions. I improved the forwarder system by utilizing RabbitMQ for message queuing and TCP connections for log transmission. This enhancement ensured reliable and efficient log forwarding, even in high-load scenarios, and improved the overall performance of the log forwarding system.

#### Improvement and Refactoring of Old, Inefficient Systems

Refactored and optimized legacy systems, such as SQL anomaly detection systems, to enhance their performance and maintainability. Some of the key improvements include enhancing the algorithm with machine learning techniques, rewriting parts of the codebase, improving database queries, and implementing more efficient algorithms. The refactoring efforts not only improved the performance of these systems but also made them easier to maintain and extend in the future.

#### Frontend Development and Enhancements

Contributed to the development and enhancement of the frontend user interface, improving user experience and accessibility. This included implementing interface for enabling/disabling parts of the system, improving the visualization of log sources, and enhancing the overall design and usability of the frontend. The frontend is built using Sinatra and Vue.js, and my contributions helped to make it more user-friendly and efficient.

#### Issue Resolution and Maintenance

Proactively addressed system issues, such as resolving sensor downtime handling, fixing bugs in the backend, API, and frontend, resolving customer-specific issues and improving the overall stability of the product. This involved reproducing the problem, identifying the root causes of issues, implementing fixes, and testing the solutions to ensure that they were effective. Regular maintenance and updates were also performed to keep the system running smoothly and to address any emerging issues.

#### Junior Developer Mentorship

Mentored junior developers, providing guidance on best practices, code reviews, and technical support. This mentorship helped to foster a collaborative and supportive development environment, ensuring that junior team members could grow their skills and contribute effectively to the team. I provided regular feedback, shared knowledge on various technologies used in the product, and assisted with problem-solving and debugging.

### Technologies Used

- Python
- Ruby
- C++
- JavaScript
- MongoDB
- RabbitMQ
- Redis
- Microsoft Azure
- Amazon AWS
- Kubernetes (Little experience)

---

# Huawei Technologies

| Job Title: |     | Global Software Service Engineer                             |
| ---------- | --- | ------------------------------------------------------------ |
| Company:   |     | [Huawei Technologies (Malaysia)](https://www.huawei.com/my/) |
| Location:  |     | Kuala Lumpur, Malaysia                                       |
| Date:      |     | 18<sup>th</sup> December 2023 - 30<sup>th</sup> April 2024   |

<br>

### Job Scope

Embarking on my role as a Global Software Service Engineer at Huawei's Global Service Resource Center (GSRC) in Malaysia has been an immersive journey, defined by continuous learning and impactful contributions.

#### Initial Learning and Certification

In my first week, I undertook a comprehensive series of learning modules and assessments, successfully earning certifications in key areas, including Information Security, Cyber Security, and Privacy Protection. These certifications, including the [Pre-Position Competence Certificate](https://minsuan96.github.io/assets/pdf/ppcc.pdf), [Cyber Security Certificate for Service Work](https://minsuan96.github.io/assets/pdf/cyber-security.pdf), and [Remote Delivery Certificate](https://minsuan96.github.io/assets/pdf/remote-delivery.pdf), laid a strong foundation for my subsequent endeavors.

#### Project Involvement - CelcomDigi Harmonization

As part of a transformative project, I am assigned to harmonize the operations of [Celcom](https://www.celcom.com.my/) and [Digi](https://www.digi.com.my/), two major network operators in Malaysia, who are undergoing a [merger](https://en.wikipedia.org/wiki/CelcomDigi). I am involved in gaining a deep understanding of Huawei's [Convergent Billing System (CBS)](https://carrier.huawei.com/en/products/service-and-software/software-business) because the project aims to update it to a new, unified system, consolidating functionalities from both companies. In the first month, I actively engaged in understanding the CBS architecture while concurrently contributing to the design of the harmonized business processes for [CelcomDigi](https://www.celcomdigi.com/).

#### Role Evolution - Testing CBS System

Transitioning to a more hands-on role, I am currently spearheading the testing phase of the harmonized and updated CBS. This involves a versatile approach, including:

1. HTTP Request Testing: Crafting and sending HTTP requests to various system interfaces, thoroughly verifying responses to ensure correctness.
2. Database Manipulation: Leveraging SQL skills for querying and updating the database, crucial for validating the system's functionality.
3. GUI Interface Testing: Directly engaging with the CBS GUI interface to assess and validate the overall performance and features of the system.

---

# The University of Edinburgh

| Job Title: |     | Java Tutor and Marker                                   |
| ---------- | --- | ------------------------------------------------------- |
| Company:   |     | [The University of Edinburgh](https://www.ed.ac.uk/)    |
| Location:  |     | Edinburgh, United Kingdom                               |
| Date:      |     | 16<sup>th</sup> January 2023 - 31<sup>th</sup> May 2023 |

<br>

### Job Scope

During my time as a student at the University of Edinburgh, I had an opportunity to become a teaching assistant as a Java Tutor and Marker for a [first-year informatics course](http://www.drps.ed.ac.uk/20-21/dpt/cxinfr08029.htm). This role, which I undertook with enthusiasm and dedication, allowed me to develop not only a deep understanding of Java programming but also honed my communication and mentorship skills.

1. Tutorial Sessions:
   - Conducted weekly tutorial sessions for a group of 10 first-year informatics students.
   - Guided students through the intricacies of the Java course materials, ensuring clarity and comprehension.
   - Encouraged active participation and engagement during the sessions.
2. Marking Duties:
   - Assumed the responsibility of assessing and marking tutorial assignments.
   - Evaluated courseworks, which contributed to the final course mark of the students.
   - Delivered constructive and insightful feedback to aid students in their academic development.
3. Feedback and Improvement:
   - Emphasized the importance of pre-session preparation, requiring students to read and complete tutorials beforehand.
   - Facilitated discussions during sessions, providing a platform for students to ask questions and seek clarification.
   - Offered personalized feedback on both tutorial answers and coursework submissions, guiding students on areas of improvement.
