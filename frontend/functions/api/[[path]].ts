import universities from '../universities.json';

export const onRequestGet: PagesFunction = async (context) => {
  const url = new URL(context.request.url);
  const path = url.pathname;

  let result: any = null;

  if (path === '/api/universities') {
    result = { data: universities };
  } else if (path === '/api/regions') {
    const regions = Array.from(new Set(universities.map((u: any) => u["지역"]))).filter(Boolean).sort();
    result = { data: regions };
  } else if (path === '/api/admission-types') {
    const types = Array.from(new Set(universities.map((u: any) => u["전형유형"]))).filter(Boolean).sort();
    result = { data: types };
  }

  if (result) {
    return new Response(JSON.stringify(result), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  }

  return new Response('Not Found', { status: 404 });
};
