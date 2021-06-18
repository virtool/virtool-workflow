from . import mock_analysis_routes, mock_index_routes, mock_job_routes, mock_subtraction_routes, mock_hmm_routes, \
    mock_sample_routes, mock_cache_routes

mock_routes = [mock_analysis_routes.mock_routes,
               mock_job_routes.mock_routes,
               mock_index_routes.mock_routes,
               mock_subtraction_routes.mock_routes,
               mock_sample_routes.mock_routes,
               mock_hmm_routes.mock_routes,
               mock_cache_routes.mock_routes]
