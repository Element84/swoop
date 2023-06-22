import http from 'k6/http';
import {check,sleep} from 'k6';

export const options = {
  stages: [
    {
      duration: '5s',
      target: 10
    },
  ],
};

export default function() {
  const swoopApiRoot = http.get('http://' + __ENV.API_HOST + '/');
  check(swoopApiRoot, {
    'status of SWOOP API root test was 200': (r) => r.status == 200
  });
  const swoopApiJobs = http.get('http://' + __ENV.API_HOST + '/jobs/');
  check(swoopApiJobs, {
    'status of SWOOP API jobs endpoint (with swoop-db) test was 200': (r) => r.status == 200
  });
  const swoopApiJobPayload = http.get('http://' + __ENV.API_HOST + '/jobs/2595f2da-81a6-423c-84db-935e6791046e/payload');
  check(swoopApiJobPayload, {
    'status of SWOOP API payload input (with object storage) test was 200': (r) => r.status == 200
  });
}
