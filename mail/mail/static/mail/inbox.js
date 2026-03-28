document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email());

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

function compose_email(email = null) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-detail-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  if (email !== null) {
    // Pre-fill fields for a reply
    document.querySelector('#compose-recipients').value = email.sender;

    let subject = email.subject;
    if (!subject.startsWith("Re: ")) {
      subject = "Re: " + subject;
    }
    document.querySelector('#compose-subject').value = subject;

    document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
  } else {
    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }
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

  // Remove any old reply button
  const old_reply_btn = document.querySelector('#reply-btn');
  if (old_reply_btn) {
    old_reply_btn.remove();
  }

  // Add reply button
  const reply_btn = document.createElement('button');
  reply_btn.id = 'reply-btn';
  reply_btn.className = 'btn btn-sm btn-outline-primary mt-2';
  reply_btn.textContent = 'Reply';
  reply_btn.addEventListener('click', () => {
    compose_email(email);
  });
  document.querySelector('#email-detail-view').appendChild(reply_btn);
}

function toggle_archive(email_id, state) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: state
    })
  }).then(() => load_mailbox('inbox'));
}