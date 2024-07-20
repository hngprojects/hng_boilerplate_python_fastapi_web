import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let successRate = new Rate('success_rate');
export let failureRate = new Rate('failure_rate');

export let options = {
	stages: [
		{ duration: '1m', target: 50 },
		{ duration: '3m', target: 50 },
		{ duration: '1m', target: 0 },
	],
	thresholds: {
		'http_req_duration': ['p(95)<500'],
		'success_rate': ['rate>0.95'],
	},
};

export default function () {
	let url = 'http://localhost:8000/api/v1/contact';
	let payload = JSON.stringify({
		name: 'Test User',
		email: 'test@example.com',
		message: 'Hello, this is a test message.',
	});

	let params = {
		headers: {
			'Content-Type': 'application/json',
		},
	};

	let res = http.post(url, payload, params);

	let success = check(res, {
		'status is 200': (r) => r.status === 200,
	});

	successRate.add(success);
	failureRate.add(!success);

	sleep(1);
}
