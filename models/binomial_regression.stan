// functions {
//     real phi(real x, real alpha, real beta, real gamma, real lambda) {
//         return gamma + (1 - gamma - lambda)/(1 + exp(-(x-alpha)/beta)));
//     }
// }
data {
    int<lower=0> X; // # of unique stimulus levels
    vector[X] x; // stimulus amplitudes
    array[X] int<lower=0> N; // stimulus counts
    array[X] int<lower=0> hits; // Hits
}
// transformed data {
//     array[X] real<lower=0, upper=1> hit_rates;
//     for (i in 1:X) {
//         hit_rates[i] = hits[i]/N[i];
//     }
// }
parameters {
  array[X] real alpha;
  real mu;
  real sigma;
  real<lower=0> sigma_err;
  real<lower=0, upper=1> gamma;
  real<lower=0, upper=1> lambda;
}
transformed parameters {
  array[X] real p = inv_logit(alpha);
}
model {
  hits ~ binomial_logit(N, alpha);
  // alpha ~ normal(mu + sigma*x, sigma_err);
  // mu ~ lognormal(6, .5);
  // sigma ~ normal(0,2);
}
// generated quantities {
//   array[X] real hit_rate;
//   for (i in 1:X) {
//     hit_rate[i] = hits[i] / N[i];
//   }
// }