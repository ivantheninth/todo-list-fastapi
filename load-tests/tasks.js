import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '30s',

    thresholds: {
        'http_req_duration{endpoint:tasks}': [
            'p(95)<100',
        ],
        'http_req_failed{endpoint:tasks}': [
            'rate<0.01',
        ],
    },
};

export function setup() {
    const loginResponse = http.post(
    'http://127.0.0.1:8000/auth/login',
    JSON.stringify({
        email: __ENV.TEST_EMAIL,
        password: __ENV.TEST_PASSWORD,
    }),
    {
        headers: {
            'Content-Type': 'application/json',
        },
        tags: {
            endpoint: 'login',
        },
    }
);

    check(loginResponse, {
        'login status is 200': (r) => r.status === 200,
    });

    const token = loginResponse.json('access_token');

    return { token };
}

export default function (data) {
    const response = http.get(
    'http://127.0.0.1:8000/tasks',
    {
        headers: {
            Authorization: `Bearer ${data.token}`,
        },
        tags: {
            endpoint: 'tasks',
        },
    }
);

    check(response, {
        'tasks status is 200': (r) => r.status === 200,
    });

    sleep(1);
}