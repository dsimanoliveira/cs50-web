document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Event listener for form submission of compose email
  document.querySelector('#compose-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    send_email(recipients, subject, body).then(() => {
      load_mailbox('sent');
    });
  });

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-detail-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-detail-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  get_emails(mailbox).then(emails => {
    console.log(emails);

    emails.forEach(email => {
      const email_element = document.createElement('div');
      email_element.className = email.read ? 'email-item read' : 'email-item unread';
      email_element.innerHTML = `
        <div><strong>${email.sender}</strong> - ${email.subject}</div>
        <div><span class="timestamp">${email.timestamp}</span></div>
      `;

      // If the mailbox is inbox, show a button that allow the user to archive the email. If the mailbox is archive, show a button that allow the user to unarchive the email.
      if (mailbox === 'inbox' || mailbox === 'archive') {
        // Show archive/unarchive button
        const archive_unarchive_button = document.createElement('button');
        archive_unarchive_button.className = 'btn btn-sm btn-outline-primary';
        archive_unarchive_button.textContent = mailbox === 'inbox' ? 'Archive' : 'Unarchive';

        archive_unarchive_button.addEventListener('click', (event) => {
          event.stopPropagation(); // Prevent the click event from propagating to the email element
          console.log('button clicked');

          // Toggle archived status
          toggle_archive(email.id, mailbox === 'inbox');

        });

        email_element.appendChild(archive_unarchive_button);
      }

      email_element.addEventListener('click', () => {
        view_email(email, mailbox);
      });

      document.querySelector('#emails-view').appendChild(email_element);
    });
  });
}

function send_email(recipients, subject, body) {
  return fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
    .then(response => response.json())
    .then(result => {
      // Print result
      console.log(result);
    });
}

function get_emails(mailbox) {
  return fetch(`/emails/${mailbox}`)
    .then(response => response.json());
}

function view_email(email, mailbox) {
  console.log(`Email ID: ${email.id} has been clicked`);

  // Mark email as read
  fetch(`/emails/${email.id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  });

  // Show email details view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-detail-view').style.display = 'block';

  // Show email details
  document.querySelector('#detail-sender').textContent = email.sender;
  document.querySelector('#detail-recipients').textContent = email.recipients.join(', ');
  document.querySelector('#detail-subject').textContent = email.subject;
  document.querySelector('#detail-timestamp').textContent = email.timestamp;
  document.querySelector('#detail-body').textContent = email.body;

  // Remove any old archive/unarchive button
  const old_btn = document.querySelector('#archive-btn');
  if (old_btn) {
    old_btn.remove();
  }

  // Create an archive/unarchive button if not in 'sent' mailbox
  if (mailbox !== 'sent') {
    const archive_btn = document.createElement('button');
    archive_btn.id = 'archive-btn';
    archive_btn.className = 'btn btn-sm btn-outline-primary mt-2';
    archive_btn.textContent = email.archived ? 'Unarchive' : 'Archive';
    archive_btn.addEventListener('click', () => {
      toggle_archive(email.id, !email.archived);
    });
    document.querySelector('#email-detail-view').appendChild(archive_btn);
  }
}

function toggle_archive(email_id, state) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: state
    })
  }).then(() => load_mailbox('inbox'));
}