Rails.application.routes.draw do
  post 'wallet/use'

  scope module: :admin, path: '/admin' do
    resources :twitter_images, except: [:show]
    resources :pairs, only: [:index, :new, :create, :destroy]
    get :twitter_image_preview, to: 'twitter_images#preview'
    get 'twitter_image_preview/:id', to: 'twitter_images#preview'
  end

  namespace :api, constraints: { ip: /127\.0\.0\.1/ } do
    resource :events, only: %i[create]
  end

  scope :soon do
    get 'landing', to: 'home#show', page: :landing
    resource :push_devices, only: %i[show create destroy]
  end

  root to: 'home#index'
end
