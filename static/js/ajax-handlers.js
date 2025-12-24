function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).on('click', '.question-vote-btn, .answer-vote-btn', function(e) {
    e.preventDefault();
    
    const btn = $(this);
    const isQuestion = btn.hasClass('question-vote-btn');
    const voteType = btn.data('vote-type');
    const ratingElement = btn.closest('.voting').find('.likes-count');
    
    const data = {
        vote_type: voteType,
        csrfmiddlewaretoken: csrftoken
    };
    
    if (isQuestion) {
        data.question_id = btn.data('question-id');
    } else {
        data.answer_id = btn.data('answer-id');
    }
    
    $.ajax({
        url: isQuestion ? '/ajax/vote-question/' : '/ajax/vote-answer/',
        method: 'POST',
        data: data,
        success: function(response) {
            if (response.status === 'success') {
                ratingElement.text(response.rating);
                
                const votingContainer = btn.closest('.voting');
                const selector = isQuestion ? '.question-vote-btn' : '.answer-vote-btn';
                votingContainer.find(selector).removeClass('active');
                
                if (response.user_vote) {
                    votingContainer.find(`${selector}[data-vote-type="${response.user_vote}"]`).addClass('active');
                }
            }
        },
        error: function(xhr) {
            if (xhr.status === 401) {
                window.location.href = '/login/';
            } else {
                const response = xhr.responseJSON;
                alert(response ? response.message : 'An error occurred');
            }
        }
    });
});

$(document).on('click', '.mark-correct-btn', function(e) {
    e.preventDefault();
    
    const btn = $(this);
    const answerId = btn.data('answer-id');
    
    $.ajax({
        url: '/ajax/mark-correct/',
        method: 'POST',
        data: {
            answer_id: answerId,
            csrfmiddlewaretoken: csrftoken
        },
        success: function(response) {
            if (response.status === 'success') {
                if (response.is_correct) {
                    btn.addClass('checked');
                    btn.find('input[type="checkbox"]').prop('checked', true);
                } else {
                    btn.removeClass('checked');
                    btn.find('input[type="checkbox"]').prop('checked', false);
                }
            }
        },
        error: function(xhr) {
            if (xhr.status === 401) {
                window.location.href = '/login/';
            } else {
                const response = xhr.responseJSON;
                alert(response ? response.message : 'An error occurred');
            }
        }
    });
});
