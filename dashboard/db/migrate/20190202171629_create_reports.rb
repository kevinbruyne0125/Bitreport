# frozen_string_literal: true

class CreateReports < ActiveRecord::Migration[5.2]
  def change
    create_table :reports do |t|
      t.references :pair
      t.integer :limit, null: false, default: 100
      t.integer :timeframe, null: false, default: 6
      t.string :indicators, array: true, null: false, default: []
      t.decimal :levels, array: true, null: false, default: []
      t.text :comment
      t.text :plot_data

      t.timestamps
    end

    add_reference :twitter_images, :reports
  end
end
