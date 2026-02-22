package cmd

import (
	"log"

	"github.com/joho/godotenv"
	"github.com/spf13/cobra"
)

func NewConfigCmd() *cobra.Command {
	var token string
	var port string
	configCmd := &cobra.Command{
		Use:   "config",
		Short: "Configurate",
		Run: func(cmd *cobra.Command, args []string) {
			env := map[string]string{"token": token, "port": port}
			if err := godotenv.Write(env, ".env"); err != nil {
				log.Print("No .env file found")
			}
		},
	}
	configCmd.Flags().StringVarP(&token, "token", "t", "", "Токен tg бота")
	// configCmd.Flags().StringVarP(&port, "port", "p", "8080", "Порт для вебхука")
	return configCmd
}
